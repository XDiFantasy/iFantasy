from flask import Blueprint
from flask_restful import Api, Resource, reqparse, fields, marshal_with
from app import db
from app.model import Recruit,User
import datetime

recruit_bp = Blueprint('recruit_bp', __name__)
recruit_api = Api(recruit_bp)
parser = reqparse.RequestParser()
query = db.session.query
add = db.session.add
commit = db.session.commit

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
    '''
    fetch recruit num and time to recruit freely
    return {num:num of recruit to get one player,
            time:xx:xx:xx or null if ready to recruit freely}
    '''
    def get(self):
        args = parser.parse_args()
        info = query(Recruit).get(args['user_id'])
        if info is None:
            return {"error": "no such user"}
        delta = (datetime.datetime.now()-info.time)
        delta = datetime.timedelta(days=delta.days, seconds=delta.seconds)
        info = {'num': 3 - info.num}
        if delta.days > 0 or delta.seconds > 18000:
            info['time'] = None
        else:
            info['time'] = str(delta)
        return info


class Onereruit(Resource):
    def post(self):
        args = parser.parse_args()
        r_info = query(Recruit).get(args['user_id'])
        u_info = query(User).get(args['user_id'])
        delta = (datetime.datetime.now()-r_info.time)
        delta = datetime.timedelta(days=delta.days, seconds=delta.seconds)
        if delta.days > 0 or delta.seconds > 18000:
            r_info.time = datetime.datetime.now()
        else:
            if u_info.money > 100:
                u_info.money -= 100
            else:
                return {"error": "no enough money"}
        if r_info.num == 3:
            getOnePlayer()
        else:
            gettrop()
        r_info.num = (r_info.num+1)%4
        commit()
        pass


recruit_api.add_resource(GetRecruit,'/get_recruit_info')
# recruit_api.add_resource(OneRecruit,'/one_recruit')
# recruit_api.add_resource(FiveRecruie,'/five_recruit')
# recruit_api.add_resource(RecruitPlayer,'/recruit')
# recruit_api.add_resource(ShowPlayer,'/show_all_payer')