from flask import Flask
from extensions import db
from flask_cors import CORS
from views.user import UsersAPI, UserDetailAPI
from views.blogs import BlogsAPI, BlogDetailAPI
from views.comments import CommentsAPI, CommentDetailAPI

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

#Rutas para Users------

app.add_url_rule(
    '/users',
    view_func=UsersAPI.as_view('users_api'),
    methods=['POST', 'GET']
)

app.add_url_rule(
    '/users/<int:user_id>',
    view_func=UserDetailAPI.as_view('user_detail_api'),
    methods=['GET', 'PUT', 'PATCH', 'DELETE']
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
