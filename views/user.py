from flask.views import MethodView
from flask import request, jsonify
from extensions import db
from datetime import datetime
from flask_jwt_extended import get_jwt, jwt_required, get_jwt_identity, create_access_token
from passlib.hash import bcrypt
from models import Users, UserCredentials
from schemas import UserSchema,RegisterSchema
from marshmallow import ValidationError


#---------------------- Clase UsersAPI: /users --------------------

class UsersAPI(MethodView):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        all_users = Users.query.all()
        return jsonify({'users': UserSchema(many=True).dump(all_users)}), 200

    def post(self):
        try:
            user_data = RegisterSchema().load(request.json)
            print("Datos recibidos en POST:", user_data)

            if Users.query.filter_by(username=user_data["username"]).first():
                return jsonify({"mensaje": "El nombre de usuario ya está en uso"}), 400
            if Users.query.filter_by(email=user_data["email"]).first():
                return jsonify({"mensaje": "El correo electrónico ya está registrado"}), 400

            new_user = Users(
                username=user_data["username"],
                email=user_data["email"],
                created_at=datetime.utcnow(),
                role=user_data.get("role", "user")
            )
            db.session.add(new_user)
            db.session.flush()  

            credentials = UserCredentials(
                user_id=new_user.id,
                password_hash=bcrypt.hash(user_data["password"]),
                role=new_user.role
            )
            db.session.add(credentials)
            db.session.commit()

            return jsonify({
                "mensaje": "Usuario creado exitosamente",
                "usuario": {
                    "id": new_user.id,
                    "username": new_user.username,
                    "email": new_user.email,
                    "role": new_user.role,
                    "created_at": new_user.created_at
                }
            }), 201

        except ValidationError as err:
            return jsonify({
                "mensaje": "Error en la validación de datos",
                "errores": err.messages
            }), 400

        except Exception as e:
            db.session.rollback()
            print("Error interno en POST /users:", e)
            return jsonify({
                "mensaje": "Error interno del servidor",
                "error": str(e)
            }), 500


#---------------- Clase UserDetailAPI: /users/<user_id>-----------------------

class UserDetailAPI(MethodView):
    @jwt_required()
    def get(self, user_id):
        current_user_id = get_jwt_identity()
        user = Users.query.get(user_id)
        if not user:
            return jsonify({'Mensaje': 'Usuario no encontrado'}), 404

        cred = UserCredentials.query.filter_by(user_id=user.id).first()
        user_dict = UserSchema().dump(user)
        if cred:
            user_dict['role'] = cred.role
        
        return jsonify(user_dict), 200

    def put(self, user_id):
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
            print("Error en PUT:", str(e))
            return jsonify({'Mensaje': 'Error interno del servidor', 'Error': str(e)}), 500

    def patch(self, user_id):
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
        user = Users.query.get(user_id)
        if not user:
            return jsonify({'Mensaje': 'Usuario no encontrado'}), 404

        try:
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