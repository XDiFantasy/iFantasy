from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from .config import config
from flask_appbuilder import AppBuilder


db = SQLAlchemy()
appbuilder = AppBuilder()
api_version = 'v1'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    print(app.config['SQLALCHEMY_DATABASE_URI'])
    db.app = app
    db.init_app(app)
    from app.controller.index import MyIndexView
    appbuilder.init_app(app,db.session, indexview=MyIndexView)
    
    from app.controller import Auth,UserError,Message
    from app.model import User
    #@app.before_request
    #def before_request():
    #    user_id = request.form.get('user_id')
    #    token = request.headers.get('Authorization')
    #    if not Auth.authToken(user_id, token):
    #        return str(Message(None, *UserError.AUTH_FAILED))

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


