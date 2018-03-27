from flask import Blueprint
from flask_restful import Api, Resource

team_bp = Blueprint("team_bp",__name__)
team_api = Api(team_bp)
