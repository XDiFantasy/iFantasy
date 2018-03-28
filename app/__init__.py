from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from .config import config

db = SQLAlchemy()

api_version = 'v1'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    print(app.config['SQLALCHEMY_DATABASE_URI'])
    db.init_app(app)
    from .controller import user_bp, bag_bp, game_bp, \
        tactics_bp, team_bp, activity_bp, chat_bp, recruit_bp
    app.register_blueprint(user_bp, url_prefix='/api/v1/user')
    app.register_blueprint(game_bp, url_prefix="/api/v1/game")
    app.register_blueprint(bag_bp, url_prefix="/api/v1/bag")
    app.register_blueprint(tactics_bp, url_prefix="/api/v1/tactics")
    app.register_blueprint(team_bp, url_prefix="/api/v1/team")
    app.register_blueprint(activity_bp, url_prefix="/api/v1/activity")
    app.register_blueprint(chat_bp, url_prefix="/api/v1/chat")
    app.register_blueprint(recruit_bp, url_prefix="/api/v1/recruit")

    return app
