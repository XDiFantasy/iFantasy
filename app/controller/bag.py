from flask import Blueprint
from flask_restful import Api, Resource

bag_bp = Blueprint('bag_bp',__name__)
bag_api = Api(bag_bp)

#your code