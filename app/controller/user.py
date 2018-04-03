from flask import Blueprint
from flask_restful import Api, Resource, reqparse

from app.controller import Message
from app.controller.utils import MobSMS
from ..config import sms_key
import hashlib
from app.config import Config
from app.model import User
import base64
import json
import time

user_bp = Blueprint("user_bp", __name__)
user_api = Api(user_bp)

parse = reqparse.RequestParser()
parse.add_argument('phone', type=str)
parse.add_argument('code', type=str)
parse.add_argument('zone', type=str)


class Auth:
    header = {'typ': 'JWT', 'alg': 'HS256'}
    payload = {
        'iss': 'iFantasy',
        'exp': None,
        'name': None
    }

    @staticmethod
    def createToken(user_id):

        user = User.query.fileter_by(id=user_id).first()
        if not user:
            raise Exception(UserError.ILLEGAL_USER)

        header = base64.urlsafe_b64decode(
            bytes(json.dumps(Auth.header), encoding='utf-8')
        )
        Auth.payload['exp'], Auth.payload['name'] = str(time.time()), str(user_id)
        payload = base64.urlsafe_b64encode(
            bytes(json.dumps(Auth.payload), encoding='utf-8')
        )
        Auth.payload['exp'], Auth.payload['name'] = None, None
        sha256 = hashlib.sha256()
        sha256.update(header)
        sha256.update(payload)
        sha256.update(Config.SECRET_KEY)
        token = header + b'.' + payload + b'.' + sha256.hexdigest()
        return token

    @staticmethod
    def authToken(user_id, token):
        user = User.query.fileter_by(id=user_id).first()
        if not user:
            return False
        if user.token == token:
            return True
        return False


class UserError:
    ILLEGAL_USER = "Illegal user", -3
    AUTH_FAILED = "Authentication Failed", -3


class UserApi(Resource):

    def post(self):
        args = parse.parse_args(strict=True)
        phone = args['phone']
        code = args['code']
        zone = args['zone']

        res = MobSMS(sms_key).verify_sms_code(zone, phone, code)
        if res == 200:
            return Message(None, None, 200).response
        elif res == 467:
            return Message(None, "请求校验验证码频繁", 467).response
        elif res == 468:
            return Message(None, "验证码错误", 468).response


user_api.add_resource(UserApi, '/verification')
