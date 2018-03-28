from flask import Blueprint
from flask_restful import Api, Resource
from app.model import Theme

activity_bp = Blueprint('activity_bp', __name__)
activity_api = Api(activity_bp)

# your code
class allThemes(Resource):
	def get(self):
		rows = Theme.query.all()
		return rows
activity_api.add_resource(allThemes,'/')