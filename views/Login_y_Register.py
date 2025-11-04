from flask import request, jsonify
from extensions import db
from models import Users
from schemas import RegisterSchema, LoginSchema, UserSchema
from marshmallow import ValidationError
from flask.views import MethodView
from passlib.hash import bcrypt
from flask_jwt_extended import create_access_token
from models import UserCredentials

class RegisterAPI(MethodView):
    def post(self):
        try:
            data = RegisterSchema().load(request.json)
        except ValidationError as err:
            return jsonify({"error": err.messages}), 400

        # Verificar si ya existe el email
        if Users.query.filter_by(email=data["email"]).first():
            return jsonify({"error": "El email ya está registrado"}), 400

        # Crear el usuario
        new_user = Users(
            username=data["username"],
            email=data["email"],
            role=data["role"]
        )
        db.session.add(new_user)
        db.session.flush()  # necesario para obtener el ID antes del commit

        # Crear credenciales
        password_hash = bcrypt.hash(data["password"])
        credentials = UserCredentials(
            user_id=new_user.id,
            password_hash=password_hash
        )
        db.session.add(credentials)
        db.session.commit()

        return jsonify({"message": "Usuario registrado exitosamente"}), 201
    

class LoginAPI(MethodView):
    def post(self):
        try:
            data = LoginSchema().load(request.json)
        except ValidationError as err:
            return jsonify({"error": err.messages}), 400

        user = Users.query.filter_by(email=data["email"]).first()

        if not user or not user.credentials:
            return jsonify({"error": "Credenciales inválidas"}), 401
        
        if not bcrypt.verify(data["password"], user.credentials.password_hash):
            return jsonify({"error": "Credenciales inválidas"}), 401
        
        access_token = create_access_token(identity=user.id)
        return jsonify({"access_token": access_token}), 200