from flask.views import MethodView
from flask import request, jsonify 
from extensions import db
from models import Comment
from schemas import CommentSchema
from marshmallow import ValidationError

class CommentsAPI(MethodView):
    def get(self):
        all_comments = Comment.query.all()
        return {'comments': CommentSchema(many=True).dump(all_comments)}, 200

    def post(self):
        try:
            comment_data = CommentSchema().load(request.json)
            new_comment = Comment(
                content=comment_data['content'],
                user_id=comment_data['user_id'],
                blog_id=comment_data['blog_id']
            )
            db.session.add(new_comment)
            db.session.commit()
            return CommentSchema().dump(new_comment), 201
        except ValidationError as err:
            return {'Mensaje': f'Error en la validación: {err.messages}'}, 400
        
class CommentDetailAPI(MethodView):
    def get(self, comment_id):
        comment = Comment.query.get(comment_id)
        if not comment:
            return {'Mensaje': 'Comentario no encontrado'}, 404
        return CommentSchema().dump(comment), 200

    def put(self, comment_id):
        comment = Comment.query.get(comment_id)
        if not comment:
            return {'Mensaje': 'Comentario no encontrado'}, 404
        try:
            comment_data = CommentSchema().load(request.json)
            comment.content = comment_data['content']
            comment.user_id = comment_data['user_id']
            comment.blog_id = comment_data['blog_id']
            db.session.commit()
            return CommentSchema().dump(comment), 200
        except ValidationError as err:
            return {'Mensaje': f'Error en la validación: {err.messages}'}, 400
    def patch(self, comment_id):
        comment = Comment.query.get(comment_id)
        if not comment:
            return {'Mensaje': 'Comentario no encontrado'}, 404
        try:
            comment_data = CommentSchema().load(request.json, partial=True)
            for key, value in comment_data.items():
                if hasattr(comment, key):  # Solo actualizar atributos existentes
                    setattr(comment, key, value)
            db.session.commit()
            return CommentSchema().dump(comment), 200
        except ValidationError as err:
            return {'Mensaje': f'Error en la validación: {err.messages}'}, 400
    def delete(self, comment_id):
        comment = Comment.query.get(comment_id)
        if not comment:
            return {'Mensaje': 'Comentario no encontrado'}, 404
        db.session.delete(comment)
        db.session.commit()
        return {'Mensaje': 'Comentario eliminado correctamente'}, 200