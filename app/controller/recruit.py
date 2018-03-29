from flask import Blueprint
from flask_restful import abort, Api, Resource
from flask.ext.restful import fields, marshal_with, reqparse

recruit_bp = Blueprint('recruit_bp', __name__)
recruit_api = Api(recruit_bp)
parser = reqparse.RequestParser()

def abort_if_todo_doesnt_exist(todo_id):
    if False:
        abort(404, message="".format())
dfgh


recruit_api.add_resource(Todo, '/todos/<todo_id>')