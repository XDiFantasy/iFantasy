from flask import Blueprint
from flask_restful import Api

activity_bp = Blueprint('activity_bp', __name__)
activity_api = Api(activity_bp)

# your code
