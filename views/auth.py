from flask import request, jsonify
from flask.views import MethodView
from extensions import db
from passlib.hash import bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import Users, UserCredentials


class RegisterAPI(MethodView):
    def post(self):
        data = request.get_json()

        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        if not all([username, email, password]):
            return jsonify({"error": "Todos los campos son obligatorios"}), 400

        if Users.query.filter_by(username=username).first():
            return jsonify({"error": "El nombre de usuario ya existe"}), 400

        if Users.query.filter_by(email=email).first():
            return jsonify({"error": "El correo ya está registrado"}), 400

        password_hash = bcrypt.hash(password)

        new_user = Users(username=username, email=email)
        db.session.add(new_user)
        db.session.commit()

        credentials = UserCredentials(
            user_id=new_user.id,
            password_hash=password_hash,
            role="user"
        )
        db.session.add(credentials)
        db.session.commit()

        return jsonify({"message": "Usuario registrado correctamente"}), 201


class LoginAPI(MethodView):
    def post(self):
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        user = Users.query.filter_by(email=email).first()
        if not user or not user.credentials:
            return jsonify({"error": "Usuario no encontrado"}), 404

        if not bcrypt.verify(password, user.credentials.password_hash):
            return jsonify({"error": "Contraseña incorrecta"}), 401

        # Crear token JWT
        access_token = create_access_token(identity={"id": user.id, "username": user.username, "role": user.role})

        return jsonify({
            "message": "Inicio de sesión exitoso",
            "access_token": access_token
        }), 200
