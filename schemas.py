from marshmallow import Schema, fields

class UserSchema(Schema):

    id = fields.Int(dump_only=True)
    email = fields.Email(required=True)
    username = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    role = fields.Str(load_default='user')

    blogs = fields.Nested('BlogSchema', many=True, dump_only=True)
    comments = fields.Nested('CommentSchema', many=True, dump_only=True)

    
from marshmallow import Schema, fields

class BlogSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    description = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)

    # ⚙️ El user_id no se carga desde el cliente (lo tomás con get_jwt_identity())
    user_id = fields.Int(dump_only=True)

    # category_id es opcional, y puede venir vacío
    category_id = fields.Int(allow_none=True)

    # Relaciones
    author = fields.Nested("UserSchema", only=["id", "username"], dump_only=True)
    category = fields.Nested("CategorySchema", only=["id", "name"], dump_only=True)
    comments = fields.Nested("CommentSchema", many=True, dump_only=True)

    
class CommentSchema(Schema):
    id = fields.Int(dump_only=True)
    description = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    user_id = fields.Int(required=True)
    blog_id = fields.Int(required=True)

class CategorySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    slug = fields.Str()
    description = fields.Str(allow_none=True)

class RegisterSchema(Schema):
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)
    role = fields.Str(required=True)

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)