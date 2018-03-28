from flask import Blueprint
from flask_restful import Api, Resource

tactics_bp = Blueprint("tactics_bp", __name__)
tactics_api = Api(tactics_bp)
