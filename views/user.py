from flask.views import MethodView
from flask import request, jsonify
from extensions import db
from datetime import datetime
from flask_jwt_extended import get_jwt, jwt_required
from passlib.hash import bcrypt
from models import Users, UserCredentials
from schemas import UserSchema
from marshmallow import ValidationError


# ---------------------------
# Clase UsersAPI: /users
# ---------------------------
class UsersAPI(MethodView):
    def get(self):
        """Obtener todos los usuarios"""
        all_users = Users.query.all()
        return jsonify({'users': UserSchema(many=True).dump(all_users)}), 200

    def post(self):
        """Crear un nuevo usuario con credenciales encriptadas"""
        try:
            # Validar los datos
            user_data = UserSchema().load(request.json)
            print("Datos recibidos en POST:", user_data)

            # Crear usuario
            new_user = Users(
                username=user_data['username'],
                email=user_data['email'],
                created_at=datetime.utcnow()
            )
            db.session.add(new_user)
            db.session.flush()  # Para obtener el id antes de crear credenciales

            # Crear credenciales con bcrypt
            credentials = UserCredentials(
                password_hash=bcrypt.hash(user_data['password']),
                role=user_data.get('role', 'user'),  # Default 'user'
                user_id=new_user.id
            )
            db.session.add(credentials)
            db.session.commit()

            return UserSchema().dump(new_user), 201

        except ValidationError as err:
            return jsonify({'Mensaje': 'Error en la validación', 'Errores': err.messages}), 400

        except Exception as e:
            db.session.rollback()
            print("Error interno en POST /users:", e)
            return jsonify({'Mensaje': 'Error interno del servidor', 'Error': str(e)}), 500


# ---------------------------
# Clase UserDetailAPI: /users/<user_id>
# ---------------------------
class UserDetailAPI(MethodView):
    
    def get(self, user_id):
        """Obtener un usuario por id"""
        user = Users.query.get(user_id)
        if not user:
            return jsonify({'Mensaje': 'Usuario no encontrado'}), 404

        # Obtener el role desde UserCredentials
        cred = UserCredentials.query.filter_by(user_id=user.id).first()
        user_dict = UserSchema().dump(user)
        if cred:
            user_dict['role'] = cred.role
        
        return jsonify(user_dict), 200

    def put(self, user_id):
        """Actualizar un usuario completamente"""
        user = Users.query.get(user_id)
        if not user:
            return jsonify({'Mensaje': 'Usuario no encontrado'}), 404

        try:
            user_data = UserSchema(partial=True).load(request.json)

            # Actualizar campos del usuario
            if 'username' in user_data:
                user.username = user_data['username']
            if 'email' in user_data:
                user.email = user_data['email']

            # Obtener credenciales para actualizar role y password
            cred = UserCredentials.query.filter_by(user_id=user.id).first()
            
            if 'role' in user_data and cred:
                cred.role = user_data['role']

            if 'password' in user_data and cred:
                cred.password_hash = bcrypt.hash(user_data['password'])

            db.session.commit()
            
            # Devolver el usuario actualizado con su role
            user_dict = UserSchema().dump(user)
            if cred:
                user_dict['role'] = cred.role
            
            return jsonify(user_dict), 200

        except ValidationError as err:
            db.session.rollback()
            return jsonify({'Mensaje': 'Error en la validación', 'Errores': err.messages}), 400
        except Exception as e:
            db.session.rollback()
            print("Error en PUT:", str(e))
            return jsonify({'Mensaje': 'Error interno del servidor', 'Error': str(e)}), 500

    def patch(self, user_id):
        """Actualizar parcialmente un usuario"""
        user = Users.query.get(user_id)
        if not user:
            return jsonify({'Mensaje': 'Usuario no encontrado'}), 404

        try:
            user_data = UserSchema(partial=True).load(request.json)

            if 'username' in user_data:
                user.username = user_data['username']
            if 'email' in user_data:
                user.email = user_data['email']
            
            cred = UserCredentials.query.filter_by(user_id=user.id).first()
            
            if 'role' in user_data and cred:
                cred.role = user_data['role']
            if 'password' in user_data and cred:
                cred.password_hash = bcrypt.hash(user_data['password'])

            db.session.commit()
            
            user_dict = UserSchema().dump(user)
            if cred:
                user_dict['role'] = cred.role
                
            return jsonify(user_dict), 200

        except ValidationError as err:
            db.session.rollback()
            return jsonify({'Mensaje': 'Error en la validación', 'Errores': err.messages}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({'Mensaje': 'Error interno', 'Error': str(e)}), 500

    def delete(self, user_id):
        """Eliminar un usuario"""
        user = Users.query.get(user_id)
        if not user:
            return jsonify({'Mensaje': 'Usuario no encontrado'}), 404

        try:
            # También eliminar credenciales asociadas
            credentials = UserCredentials.query.filter_by(user_id=user.id).first()
            if credentials:
                db.session.delete(credentials)

            db.session.delete(user)
            db.session.commit()
            return jsonify({'Mensaje': 'Usuario eliminado correctamente'}), 200
        except Exception as e:
            db.session.rollback()
            print("Error al eliminar:", str(e))
            return jsonify({'Mensaje': 'Error al eliminar usuario', 'Error': str(e)}), 500