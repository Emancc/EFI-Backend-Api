from marshmallow import Schema, fields

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    password = fields.Str(load_only=True, required=True)
    email = fields.Email(required=True)
    username = fields.Str(required=True)
    blogs = fields.Nested('BlogSchema', many=True, dump_only=True)
    comments = fields.Nested('CommentSchema', many=True, dump_only=True)

class BlogSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    description = fields.Str(required=True)  # Cambiado de 'content' a 'description' para coincidir con el modelo
    created_at = fields.DateTime(dump_only=True)
    user_id = fields.Int(required=True)  # Cambiado de 'author_id' a 'user_id' para coincidir con el modelo
    category_id = fields.Int(required=False)  # Añadido para manejar la relación con categorías
    comments = fields.Nested('CommentSchema', many=True, dump_only=True)
    
class CommentSchema(Schema):
    id = fields.Int(dump_only=True)
    description = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    user_id = fields.Int(required=True)
    blog_id = fields.Int(required=True)



