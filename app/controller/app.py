from flask import Blueprint, request
from flask_restful import Api, Resource

import sh

app_bp = Blueprint("app_bp", __name__)
app_api = Api(app_bp)


class AutoDeployApi(Resource):

    def post(self):
        sh.Command('reuwsgi\r')
        sh.Command('exit\r')


app_api.add_resource(AutoDeployApi, '/auto_deploy')