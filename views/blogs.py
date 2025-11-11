from flask.views import MethodView
from flask import request, jsonify
from extensions import db
from models import Blogs,Category
from flask_jwt_extended import jwt_required, get_jwt_identity
from schemas import BlogSchema
from marshmallow import ValidationError


class BlogsAPI(MethodView):
    def get(self):
        all_blogs = Blogs.query.all()
        return {'blogs': BlogSchema(many=True).dump(all_blogs)}, 200
    
    @jwt_required()
    def post(self):
        try:
            # Validar datos del request sin user_id (lo tomamos del JWT)
            blog_data = BlogSchema(exclude=["user_id"]).load(request.json)
            current_user_id = get_jwt_identity()

            # Obtener category_id si viene
            category_id = blog_data.get('category_id')

            # 🔹 Validar si la categoría existe (solo si se envía)
            if category_id:
                from models import Category  # importar aquí para evitar import circular
                category = Category.query.get(category_id)
                if not category:
                    return {
                        "Mensaje": f"La categoría con id {category_id} no existe."
                    }, 400

            # Crear nuevo blog
            new_blog = Blogs(
                title=blog_data['title'],
                description=blog_data['description'],
                user_id=current_user_id,
                category_id=category_id  # puede ser None
            )

            db.session.add(new_blog)
            db.session.commit()

            return BlogSchema().dump(new_blog), 201

        except ValidationError as err:
            return {'Mensaje': f'Error en la validación: {err.messages}'}, 400

        except Exception as e:
            # 🔹 Captura cualquier otro error de BD o integridad
            db.session.rollback()
            return {'Mensaje': f'Error al crear el blog: {str(e)}'}, 500

        

class BlogDetailAPI(MethodView):
    @jwt_required()
    def get(self, blog_id):
        blog = Blogs.query.get(blog_id)
        if not blog:
            return {'Mensaje': 'Blog no encontrado'}, 404
        return BlogSchema().dump(blog), 200

    def put(self, blog_id):
        blog = Blogs.query.get(blog_id)
        if not blog:
            return {'Mensaje': 'Blog no encontrado'}, 404
        try:
            blog_data = BlogSchema().load(request.json)
            blog.title = blog_data['title']
            blog.description = blog_data['description']
            blog.user_id = blog_data['user_id']
            if 'category_id' in blog_data:
                blog.category_id = blog_data['category_id']
            db.session.commit()
            return BlogSchema().dump(blog), 200
        except ValidationError as err:
            return {'Mensaje': f'Error en la validación: {err.messages}'}, 400

    def patch(self, blog_id):
        blog = Blogs.query.get(blog_id)
        if not blog:
            return {'Mensaje': 'Blog no encontrado'}, 404
        try:
            blog_data = BlogSchema().load(request.json, partial=True)
            for key, value in blog_data.items():
                if hasattr(blog, key):  # Solo actualizar atributos existentes
                    setattr(blog, key, value)
            db.session.commit()
            return BlogSchema().dump(blog), 200
        except ValidationError as err:
            return {'Mensaje': f'Error en la validación: {err.messages}'}, 400

    def delete(self, blog_id):
        blog = Blogs.query.get(blog_id)
        if not blog:
            return {'Mensaje': 'Blog no encontrado'}, 404
        db.session.delete(blog)
        db.session.commit()
        return {'Mensaje': 'Blog eliminado correctamente'}, 200