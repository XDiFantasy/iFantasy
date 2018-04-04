import base64
import hashlib
import json
import re
import time

from flask import Blueprint, request
from flask_restful import Api, Resource, reqparse

from app import db
from app.config import Config
from app.controller import Message
from app.controller.utils import MobSMS
from app.model import User
from ..config import sms_key

user_bp = Blueprint("user_bp", __name__)
user_api = Api(user_bp)
parser = reqparse.RequestParser()
query = db.session.query
add = db.session.add
commit = db.session.commit
rollback = db.session.rollback


class Auth:
    header = {'typ': 'JWT', 'alg': 'HS256'}
    payload = {
        'iss': 'iFantasy-android',
        'exp': None,
        'name': None
    }

    @staticmethod
    def generateTempToken(phone):
        header = base64.urlsafe_b64encode(
            bytes(json.dumps(Auth.header), encoding='utf-8')
        )
        Auth.payload['exp'], Auth.payload['name'] = str(time.time()), str(phone)
        payload = base64.urlsafe_b64encode(
            bytes(json.dumps(Auth.payload), encoding='utf-8')
        )
        Auth.payload['exp'], Auth.payload['name'] = None, None
        sha256 = hashlib.sha256()
        sha256.update(header)
        sha256.update(payload)
        sha256.update(base64.urlsafe_b64encode(Config.SECRET_KEY))
        temptoken = header + b'.' + payload + b'.' + bytes(sha256.hexdigest(), encoding='utf-8')
        user = User(None, phone, None, None, temptoken, None)
        add(user)
        return json.dumps(user)

    @staticmethod
    def generateLoginToken(user_id):
        user = query.get(user_id)
        if not user:
            return Message(None, UserError.ILLEGAL_USER).response

        header = base64.urlsafe_b64encode(
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
        sha256.update(base64.urlsafe_b64encode(Config.SECRET_KEY))
        logintoken = header + b'.' + payload + b'.' + bytes(sha256.hexdigest(), encoding='utf-8')
        user.logintoken = logintoken
        return json.dumps(user)

    @staticmethod
    def generateAccessToken(user_id):
        user = query.get(user_id)
        if not user:
            raise Exception(UserError.ILLEGAL_USER)

        header = base64.urlsafe_b64encode(
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
        sha256.update(base64.urlsafe_b64encode(Config.SECRET_KEY))
        accesstoken = header + b'.' + payload + b'.' + bytes(sha256.hexdigest(), encoding='utf-8')
        user.accesstoken = accesstoken
        mes = Message(json.dumps(user), None, 200)
        try:
            commit()
        except Exception as e:
            rollback()
            print(e)
            mes = Message(None, "cannot commit to db", -1)
        return mes.response

    @staticmethod
    def authLoginToken(phone, logintoken):
        user = query.fileter_by(tel=phone).first()
        return user and logintoken == user.logintoken

    @staticmethod
    def authAccessToken(user_id, accesstoken):
        user = query.get(user_id)
        return user and accesstoken == user.accesstoken


class UserError:
    ILLEGAL_USER = "Illegal user", -3
    AUTH_FAILED = "Authentication Failed", -3


class VerificationApi(Resource):
    parse = reqparse.RequestParser()
    parse.add_argument('phone', type=str)
    parse.add_argument('code', type=str)
    parse.add_argument('zone', type=str)

    def post(self):
        args = self.parse.parse_args(strict=True)
        phone = args['phone']
        code = args['code']
        zone = args['zone']

        res = MobSMS(sms_key).verify_sms_code(zone, phone, code)
        if res == 200:
            user = User.query.fileter_by(tel=phone).first()
            if not user or not user.logintoken:
                mes = Message(Auth.generateTempToken(phone), None, 201)
                try:
                    commit()
                except Exception as e:
                    rollback()
                    print(e)
                    mes = Message(None, "cannot commit to db", -1)
                return mes.response
            return Message(json.dumps(user), None, 200).response
        elif res == 467:
            return Message(None, "请求校验验证码频繁", 467).response
        elif res == 468:
            return Message(None, "验证码错误", 468).response


class RegisterApi(Resource):
    parse = reqparse.RequestParser()
    parse.add_argument('phone', type=str)
    parse.add_argument('nickname', type=str)

    def post(self):
        args = self.parse.parse_args(strict=True)
        phone = args['phone']
        nickname = args['nickname']
        temptoken = request.headers.get('Authorization')

        if not Auth.authLoginToken(phone, temptoken):
            return Message(None, *UserError.AUTH_FAILED).response

        user = query.fileter_by(tel=phone).first()
        user.nickname = nickname
        mes = Message(Auth.generateLoginToken(user.id), None, 200)
        try:
            commit()
        except Exception as e:
            rollback()
            print(e)
            mes = Message(None, "cannot commit to db", -1)
        return mes.response


class LoginApi(Resource):
    parse = reqparse.RequestParser()
    parse.add_argument('phone', type=str)

    def post(self):
        args = self.parse.parse_args(strict=True)
        phone = args['phone']
        logintoken = request.headers.get('Authorization')

        if not Auth.authLoginToken(phone, logintoken):
            return Message(None, *UserError.AUTH_FAILED).response

        user = query.fileter_by(tel=phone).first()
        mes = Message(Auth.generateLoginToken(user.id), None, 200)
        try:
            commit()
        except Exception as e:
            rollback()
            print(e)
            mes = Message(None, "cannot commit to db", -1)
        return mes.response


class LogoutApi(Resource):
    parse = reqparse.RequestParser()
    parse.add_argument('user_id', type=int)

    def post(self):
        args = self.parse.parse_args(strict=True)
        user_id = args['user_id']
        user = query.get(user_id)
        user.logintoken = None
        user.accesstoken = None
        mes = Message(json.dumps(user), None, 200)
        try:
            commit()
        except Exception as e:
            rollback()
            print(e)
            mes = Message(None, "cannot commit to db", -1)
        return mes.response


user_api.add_resource(VerificationApi, '/verification')
user_api.add_resource(RegisterApi, '/register')
user_api.add_resource(LoginApi, '/login')
user_api.add_resource(LogoutApi, '/logout')
