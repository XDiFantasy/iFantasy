from flask import Blueprint
from flask_restful import Api, Resource

recruit_bp = Blueprint('recruit_bp', __name__)
recruit_api = Api(recruit_bp)

# your code

class hello(Resource):
    def get(self):
        return "hello"

recruit_api.add_resource(hello,'/')
