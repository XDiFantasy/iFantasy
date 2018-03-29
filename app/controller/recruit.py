from flask import Blueprint
from flask_restful import Api, Resource, reqparse, fields, marshal_with
from app import db
from app.model import Recruit
import datetime

recruit_bp = Blueprint('recruit_bp', __name__)
recruit_api = Api(recruit_bp)
parser = reqparse.RequestParser()
query = db.session.query

parser.add_argument('user_id',type=int,required=True,help='cannot get uer_id')


def toJson(obj):
    json = {}
    for key, value in vars(obj).items():
        if key == '_sa_instance_state':
            continue
        if type(value) in [int,str,float,bool,list,dict]:
            json[key] = value
    return json


class GetRecruit(Resource):
    def get(self):
        args = parser.parse_args()
        info = query(Recruit).get(args['user_id'])
        if info is None:
            return {"error": "no such user"}
        info.num = 3 - info.num
        delta = (datetime.datetime.now()-info.time)
        delta = datetime.timedelta(days=delta.days, seconds=delta.seconds)
        info = toJson(info)
        if delta.days > 0 or delta.seconds > 18000:
            info['time'] = None
        else:
            info['time'] = str(delta)
        return info



recruit_api.add_resource(GetRecruit,'/get_recruit_info')
# recruit_api.add_resource(OneRecruit,'/one_recruit')
# recruit_api.add_resource(FiveRecruie,'/five_recruit')
# recruit_api.add_resource(RecruitPlayer,'/recruit')
# recruit_api.add_resource(ShowPlayer,'/show_all_payer')