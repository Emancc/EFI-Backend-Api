from flask import Flask, jsonify
from extensions import db
from flask_cors import CORS
from views.user import UsersAPI, UserDetailAPI
from views.blogs import BlogsAPI, BlogDetailAPI
from views.comments import CommentsAPI, CommentDetailAPI
from views.auth import RegisterAPI, LoginAPI
from views.categories import CategoriesAPI
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta

app = Flask(__name__)
# Configuración de la aplicación
app.config['SECRET_KEY'] = 'mi_super_secreto_12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost/db_blog'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['JWT_SECRET_KEY'] = 'mi_jwt_secreto_12345'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

jwt = JWTManager(app)

CORS(
    app,
    resources={r"/*": {"origins": "http://localhost:5173"}},
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
)
db.init_app(app)

with app.app_context():
    db.create_all()

#------------------------------------MANEJO DE ERRORES JWT------------------------------------#
# -------- Errores siempre en JSON --------
@app.errorhandler(404)
def not_found(e):
    return jsonify({"Mensaje": "not_found"}), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"Mensaje": "method_not_allowed"}), 405

@app.errorhandler(500)
def server_error(e):
    return jsonify({"Mensaje": "server_error"}), 500

# -------- Respuestas JWT en JSON (sin redirecciones HTML) --------
@jwt.unauthorized_loader
def missing_jwt(err):
    return jsonify({"Mensaje": "unauthorized", "Detalle": err}), 401

@jwt.invalid_token_loader
def invalid_jwt(err):
    return jsonify({"Mensaje": "invalid_token", "Detalle": err}), 422

@jwt.expired_token_loader
def expired_jwt(jwt_header, jwt_payload):
    return jsonify({"Mensaje": "token_expired"}), 401
#------------------------------------FIN MANEJO DE ERRORES JWT------------------------------------#

#Rutas Register y login------
app.add_url_rule(
    '/register',
    view_func=RegisterAPI.as_view('register_api'),
    methods=['POST']
)

app.add_url_rule(
    '/login',
    view_func=LoginAPI.as_view('login_api'),
    methods=['POST']
)
#Rutas para Users------

users_view = UsersAPI.as_view('users_api')
app.add_url_rule('/users', view_func=users_view, methods=['GET', 'POST'])

app.add_url_rule(
    '/users/<int:user_id>',
    view_func=UserDetailAPI.as_view('user_detail_api'),
    methods=['GET', 'PUT', 'PATCH', 'DELETE']
)


#Rutas para Categories------
app.add_url_rule(
    '/categories',
    view_func=CategoriesAPI.as_view('categories_api'),
    methods=['POST', 'GET']
)

#Rutas para Blogs------

app.add_url_rule(
    '/blogs',
    view_func=BlogsAPI.as_view('blogs_api'),
    methods=['POST', 'GET']
)
app.add_url_rule(
    '/blogs/<int:blog_id>',
    view_func=BlogDetailAPI.as_view('blog_detail_api'),
    methods=['GET', 'PUT', 'PATCH', 'DELETE']
) 

#Rutas para Comments------
app.add_url_rule(
    '/comments',
    view_func=CommentsAPI.as_view('comments_api'),
    methods=['POST', 'GET']
)
app.add_url_rule(
    '/comments/<int:comment_id>',
    view_func=CommentDetailAPI.as_view('comment_detail_api'),
    methods=['GET', 'PUT', 'PATCH', 'DELETE']
)



#Rutas por cambiar
if __name__ == '__main__':
    app.run(debug=True, port=5000)
