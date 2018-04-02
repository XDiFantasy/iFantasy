from flask import Blueprint
from flask_restful import Api, Resource, reqparse, fields, marshal_with
from app import db
from app.model import Recruit,User,PlayerBase, BagPlayer
from .message import Message
from random import choice
import datetime

recruit_bp = Blueprint('recruit_bp', __name__)
recruit_api = Api(recruit_bp)
parser = reqparse.RequestParser()
query = db.session.query
add = db.session.add
commit = db.session.commit
parser.add_argument('user_id',type=int,help='cannot get uer_id')


def toJson(obj):
    json = {}
    for key, value in vars(obj).items():
        if key == '_sa_instance_state':
            continue
        if type(value) in [int,str,float,bool,list,dict]:
            json[key] = value
    return json
class Error:
    NoUser = "no such user", -250

class rMessage(Message):
    def __init__(self,result=None,error=('',0)):
        super(rMessage, self).__init__(result,error[0],error[1])


class GetRecruit(Resource):
    '''
    fetch recruit num and time to recruit freely
    return {num:num of recruit to get one player,
            time:xx:xx:xx or null if ready to recrresult=uit freely}
    '''
    def get(self):
        args = parser.parse_args()
        info = query(Recruit).get(args['user_id'])
        if info is None:
            return rMessage(error=Error.NoUser).response
        delta = (datetime.datetime.now()-info.time)
        delta = datetime.timedelta(days=delta.days, seconds=delta.seconds)
        res = {'num': 3 - info.num}
        if delta.days > 0 or delta.seconds > 18000:
            res['time'] = None
        else:
            res['time'] = str(delta)
        return rMessage(res).response

def toSet(data):
    res = set()
    for item in data:
        res.add(item[0])
    return res


def selectPlayer(type):
    score = PlayerBase.score
    id = PlayerBase.id
    if type == 1:
        res = query(id).filter(score >80).all()
    if type == 2:
        res = query(id).filter(score <=80, score >70).all()
    if type == 3:
        res = query(id).filter(score <=70).all()
    return toSet(res)

def getMidPlayer(filter):
    players = list(selectPlayer(2)-filter)
    if len(players) > 0:
        player = choice(players)
    else:
        players = list(selectPlayer(1) - filter)
        if len(players) > 0:
            player = choice(players)
        else:
            pass


def getprop():
    pass

class OneRecruit(Resource):
    def post(self):
        args = parser.parse_args()
        r_info = query(Recruit).get(args['user_id'])

        u_info = query(User).get(args['user_id'])
        b_info = query(BagPlayer.player_id).filter(BagPlayer.user_id == u_info.id).all()
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
            getMidPlayer(toSet(b_info))
        else:
            getprop()
        r_info.num = (r_info.num+1)%4
        commit()
        pass


recruit_api.add_resource(GetRecruit,'/get_recruit_info')
recruit_api.add_resource(OneRecruit,'/one_recruit')
# recruit_api.add_resource(FiveRecruie,'/five_recruit')
# recruit_api.add_resource(RecruitPlayer,'/recruit')
# recruit_api.add_resource(ShowPlayer,'/show_all_payer')