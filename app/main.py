from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config

db = SQLAlchemy()

api_version = 'v1'

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    
    from .controller.bag import bag_bp
    app.register_blueprint(bag_bp,url_prefix='/api/v1/bag')

    from controller.game import game_bp
    app.register_blueprint(game_bp,url_prefix='/api/v1/game')

    