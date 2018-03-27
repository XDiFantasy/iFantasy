from flask import Blueprint
from flask_restful import Api

game_bp = Blueprint('game_bp',__name__,static_folder="../static/game")
game_api = Api(game_bp)

