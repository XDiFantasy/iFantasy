from flask import Blueprint, jsonify
from flask_restful import Api, Resource, reqparse

from .utils import MobSMS
from ..config import sms_key

user_bp = Blueprint("user_bp", __name__)
user_api = Api(user_bp)

parse = reqparse.RequestParser()
parse.add_argument('phone', type=str)
parse.add_argument('code', type=str)
parse.add_argument('zone', type=str)


class UserApi(Resource):

    def post(self):
        args = parse.parse_args(strict=True)
        phone = args['phone']
        code = args['code']
        zone = args['zone']

        res = MobSMS(sms_key).verify_sms_code(zone, phone, code)
        if res == 200:
            return jsonify({'resutl': 'ok'})
        else:
            return jsonify({'result': 'no'})


user_api.add_resource(UserApi, '/user')
