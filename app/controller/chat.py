from flask import Blueprint
from flask_restful import Api, Resource

chart_bp = Blueprint('chart_bp',__name__)
chart_api = Api(chart_bp)

#your code