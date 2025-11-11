from extensions import db
from datetime import datetime

#---------------------- Modelos de Users --------------------
class Users(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.String(50), default='user')
    

    blogs = db.relationship('Blogs', backref='author', lazy=True)
    credentials = db.relationship('UserCredentials', back_populates='user', uselist=False)

#---------------------- Modelos de Category--------------------
class Category(db.Model):
    __tablename__ = 'category'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    slug = db.Column(db.String(60), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    blogs = db.relationship('Blogs', backref='blog_category', lazy=True)

    def __repr__(self):
        return f"<Category {self.name}>"

#---------------------- Modelos de Blogs --------------------
class Blogs(db.Model):
    __tablename__ = 'blogs'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    
    comments = db.relationship('Comment', backref='blog', lazy=True, cascade='all, delete-orphan')
    category = db.relationship('Category', back_populates='blogs') 
    
    def __repr__(self):
        return f"<Blog {self.title}>"

#---------------------- Modelos de Comments --------------------
class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    blog_id = db.Column(db.Integer, db.ForeignKey('blogs.id'), nullable=False)
    
    user = db.relationship('Users', backref=db.backref('comments', lazy=True))

    def __repr__(self):
        return f"<Comment {self.id} on Blog {self.blog_id}>"
    
#---------------------- Modelos de UserCredentials --------------------
class UserCredentials(db.Model):
    __tablename__ = 'user_credentials'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='user')
    user = db.relationship('Users', back_populates='credentials', uselist=False)

    def __str__(self)-> str:
        return f"User Credentials for user id ={self.user_id}, role={self.role}"