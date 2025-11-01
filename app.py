from flask import Flask, request, jsonify
from marshmallow import ValidationError
from extensions import db
from flask_cors import CORS
from schemas import UserSchema, BlogSchema, CommentSchema

app = Flask(__name__)
# Configuración de la aplicación
app.config['SECRET_KEY'] = 'mi_super_secreto_12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost/db_blog'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#habilitacion de CORS para la aplicacion
CORS(app)
# Inicializar la extensión db con la aplicación
db.init_app(app)

# Importar los modelos después de inicializar db
from models import Users, Blogs, Category, Comment

# Crear un contexto de aplicación para crear las tablas
with app.app_context():
    # Crear todas las tablas definidas en los modelos
    db.create_all()

@app.route('/users', methods=['POST', 'GET'])
def users():
    if request.method == 'POST':
        try:
            user_data = UserSchema().load(request.json)
            print("Datos recibidos en POST:", user_data)

            new_user = Users(
                username=user_data['username'],
                email=user_data['email'],
                role=user_data.get('role', 'user')
            )

            new_user.set_password(user_data['password'])

            db.session.add(new_user)
            db.session.commit()

            return UserSchema().dump(new_user), 201

        except ValidationError as err:
            return {'Mensaje': 'Error en la validación', 'Errores': err.messages}, 400

        except Exception as e:
            db.session.rollback()
            print("Error interno en POST /users:", e)
            return {'Mensaje': 'Error interno del servidor', 'Error': str(e)}, 500
    # Manejo para el método GET
    elif request.method == 'GET':
        all_users = Users.query.all()
        return {'users': UserSchema(many=True).dump(all_users)}, 200

    

@app.route('/users/<int:user_id>', methods=['GET', 'PATCH', 'PUT', 'DELETE'])
def user(user_id):
    user = Users.query.get(user_id)
    if user is None:
        return jsonify({'Mensaje': 'Usuario no encontrado'}), 404

    elif request.method == 'PUT':
        try:
            user_data = UserSchema().load(request.json)
            print("Datos recibidos:", user_data)

            user.username = user_data['username']
            user.email = user_data['email']

            if 'role' in user_data and user_data['role']:
                user.role = user_data['role']

            if 'password' in user_data and user_data['password']:
                user.set_password(user_data['password'])

            db.session.commit()
            return jsonify({'Mensaje': 'Usuario actualizado correctamente'}), 200

        except ValidationError as err:
            return jsonify({'Mensaje': 'Error en la validación', 'Errores': err.messages}), 400

        except Exception as e:
            db.session.rollback()
            print("Error interno en PUT /users:", e)
            return jsonify({'Mensaje': 'Error interno del servidor', 'Error': str(e)}), 500
                    

    elif request.method == 'PATCH':
        try:
            user_data = UserSchema().load(request.json, partial=True)
            for key, value in user_data.items():
                setattr(user, key, value)
            db.session.commit()
            return UserSchema().dump(user), 200
        except ValidationError as err:
            return jsonify({'Mensaje': f'Error en la validación: {err.messages}'}), 400


    elif request.method == 'DELETE':
        db.session.delete(user)
        db.session.commit()
        return jsonify({'Mensaje': 'Usuario eliminado correctamente'}), 200
    
    elif request.method == 'GET':
        return UserSchema().dump(user), 200

@app.route('/blogs', methods=['POST','GET'])
def blogs():
    if request.method == 'POST':
        try:
            blog_data = BlogSchema().load(request.json)
            new_blog = Blogs(
                title=blog_data['title'],
                description=blog_data['description'],
                user_id=blog_data['user_id'],
                category_id=blog_data.get('category_id')
            )
            db.session.add(new_blog)
            db.session.commit()
            return BlogSchema().dump(new_blog), 201
        except ValidationError as err:
            return {'Mensaje': f'Error en la validación: {err.messages}'}, 400
    
    # Manejo para el método GET
    elif request.method == 'GET':
        all_blogs = Blogs.query.all()
        return {'blogs': BlogSchema(many=True).dump(all_blogs)}, 200

@app.route('/blogs/<int:blog_id>', methods=['GET','PUT','PATCH','DELETE'])
def blog(blog_id):
    blog = Blogs.query.get(blog_id)
    if not blog:
        return {'Mensaje': 'Blog no encontrado'}, 404

    if request.method == 'PUT':
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

    elif request.method == 'PATCH':
        try:
            blog_data = BlogSchema().load(request.json, partial=True)
            for key, value in blog_data.items():
                if hasattr(blog, key):  # Solo actualizar atributos existentes
                    setattr(blog, key, value)
            db.session.commit()
            return BlogSchema().dump(blog), 200
        except ValidationError as err:
            return {'Mensaje': f'Error en la validación: {err.messages}'}, 400

    elif request.method == 'DELETE':
        db.session.delete(blog)
        db.session.commit()
        return {'Mensaje': 'Blog eliminado correctamente'}, 200
        
    elif request.method == 'GET':
        return BlogSchema().dump(blog), 200
        db.session.delete(blog)
        db.session.commit()
        return {'Mensaje': 'Blog eliminado correctamente'}, 200

    elif request.method == 'GET':
        blog = Blogs.query.get(blog_data['id'])
        return BlogSchema().dump(blog), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
