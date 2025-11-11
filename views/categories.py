from flask.views import MethodView
from models import Category
from schemas import CategorySchema

class CategoriesAPI(MethodView):
    def get(self):
        categories = Category.query.all()
        return {'categories': CategorySchema(many=True).dump(categories)}, 200
