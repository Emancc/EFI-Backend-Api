from flask.views import MethodView
from flask import request, jsonify      
from extensions import db
from models import Users
from schemas import UserSchema
from marshmallow import ValidationError


class UsersAPI(MethodView):
    def get(self):
        all_users = Users.query.all()
        return {'users': UserSchema(many=True).dump(all_users)}, 200
    
    def post(self):
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
        
class UserDetailAPI(MethodView):
    def get(self, user_id):
        user = Users.query.get(user_id)
        if user is None:
            return jsonify({'Mensaje': 'Usuario no encontrado'}), 404
        return UserSchema().dump(user), 200

    def put(self, user_id):
        user = Users.query.get(user_id)
        if user is None:
            return jsonify({'Mensaje': 'Usuario no encontrado'}), 404
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
    
    def  patch(self, user_id):
        user = Users.query.get(user_id)
        try:
            user_data = UserSchema(partial=True).load(request.json)
            if 'name' in user_data:
                user.name = user_data.get('name')
            if 'email' in user_data:
                user.email = user_data.get('email')
            db.session.commit()
            return UserSchema().dump(user), 200
        except ValidationError as err:
            return jsonify({'Mensaje': f'Error en la validación: {err.messages}'}), 400
    
    def delete(self, user_id):
        user = Users.query.get(user_id)
        if user is None:
            return jsonify({'Mensaje': 'Usuario no encontrado'}), 404
        db.session.delete(user)
        db.session.commit()
        return jsonify({'Mensaje': 'Usuario eliminado correctamente'}), 200