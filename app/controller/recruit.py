from flask import Blueprint
from flask_restful import Api, Resource

recruit_bp = Blueprint('recruit_bp',__name__)
recruit_api = Api(recruit_bp)

#your code