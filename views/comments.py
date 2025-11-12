from flask.views import MethodView
from flask import request, jsonify
from extensions import db
from models import Comment, Blogs
from schemas import CommentSchema
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError

class CommentsAPI(MethodView):
    def get(self):
        all_comments = Comment.query.all()
        return jsonify({'comments': CommentSchema(many=True).dump(all_comments)}), 200

    @jwt_required()
    def post(self):
        try:
            payload = request.get_json() or {}
            data = CommentSchema(partial=("user_id",)).load(payload)

            uid = get_jwt_identity()
            if not uid:
                return jsonify({"Mensaje": "No autenticado"}), 401

            blog = Blogs.query.get(data["blog_id"])
            if not blog:
                return jsonify({"Mensaje": "Blog no válido"}), 400

            new_comment = Comment(
                content=data["content"],
                user_id=uid,
                blog_id=data["blog_id"]
            )
            db.session.add(new_comment)
            db.session.commit()
            db.session.refresh(new_comment)

            return jsonify(CommentSchema().dump(new_comment)), 201

        except ValidationError as err:
            return jsonify({"Mensaje": "Error en la validación", "Errores": err.messages}), 400
        except IntegrityError as e:
            db.session.rollback()
            return jsonify({"Mensaje": "Integridad de datos", "Error": str(e.orig)}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({"Mensaje": "Error interno", "Error": str(e)}), 500

class CommentDetailAPI(MethodView):
    def get(self, comment_id):
        comment = Comment.query.get(comment_id)
        if not comment:
            return jsonify({'Mensaje': 'Comentario no encontrado'}), 404
        return jsonify(CommentSchema().dump(comment)), 200

    @jwt_required()
    def put(self, comment_id):
        comment = Comment.query.get(comment_id)
        if not comment:
            return jsonify({'Mensaje': 'Comentario no encontrado'}), 404
        try:
            data = CommentSchema().load(request.get_json())
            comment.content = data['content']
            comment.user_id = data['user_id']
            comment.blog_id = data['blog_id']
            db.session.commit()
            return jsonify(CommentSchema().dump(comment)), 200
        except ValidationError as err:
            return jsonify({'Mensaje': 'Error en la validación', 'Errores': err.messages}), 400

    @jwt_required()
    def patch(self, comment_id):
        comment = Comment.query.get(comment_id)
        if not comment:
            return jsonify({'Mensaje': 'Comentario no encontrado'}), 404
        try:
            data = CommentSchema().load(request.get_json(), partial=True)
            for k, v in data.items():
                if hasattr(comment, k):
                    setattr(comment, k, v)
            db.session.commit()
            return jsonify(CommentSchema().dump(comment)), 200
        except ValidationError as err:
            return jsonify({'Mensaje': 'Error en la validación', 'Errores': err.messages}), 400

    @jwt_required()
    def delete(self, comment_id):
        comment = Comment.query.get(comment_id)
        if not comment:
            return jsonify({'Mensaje': 'Comentario no encontrado'}), 404
        db.session.delete(comment)
        db.session.commit()
        return jsonify({'Mensaje': 'Comentario eliminado correctamente'}), 200
