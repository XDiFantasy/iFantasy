from flask import Blueprint
from flask_restful import Api, Resource, reqparse, fields, marshal_with
from app import db
from app.model import Recruit,User,PlayerBase, BagPlayer,BagTrailCard, BagPiece,BagProp
from .message import Message
from random import choice,random
import datetime

recruit_bp = Blueprint('recruit_bp', __name__)
recruit_api = Api(recruit_bp)
parser = reqparse.RequestParser()
query = db.session.query
add = db.session.add
commit = db.session.commit
rollback = db.session.rollback
parser.add_argument('user_id',type=int,required=True,help='cannot get uer_id')



class State:
    NoUser = "no such user", -250
    NoMoney = "no enough money", -251
    OwnPlayer = "have owned the player",-252
    FailCommit = "cannot commit to db",-201
    player = 201
    trail = 202
    piece = 203
    fund = 204
    exp =205

class rMessage(Message):
    def __init__(self,result=None,error=('',0),code=0):
        if code == 0:
            super(rMessage,self).__init__(result,error[0],error[1])
        else:
            super(rMessage,self).__init__(result,error[0],code)

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
            return rMessage(error=State.NoUser).response
        delta = (datetime.datetime.now() - info.time)
        delta = datetime.timedelta(days=delta.days, seconds=delta.seconds)
        res = {'num': 3 - info.num}
        if delta.days > 0 or delta.seconds > 18000:
            res['time'] = None
        else:
            res['time'] = str(delta)
        return rMessage(res).response



def __toList__(data):
    res = list()
    for item in data:
        res.append(item[0])
    return res

def __toSet__(data):
    res = set()
    for item in data:
        res.add(item[0])
    return res

def __randomPick__(lists, prob):
    r = random()
    cum = 0.0
    for item, item_prob in zip(lists, prob):
        cum += item_prob  
        if r < cum:break
    return item  

def selectPlayer(type):
    score = PlayerBase.score
    id = PlayerBase.id
    if type == 0:
        res = query(id).filter(score > 90).all()
    if type == 1:
        res = query(id).filter(score <=90, score >80).all()
    if type == 2:
        res = query(id).filter(score <=80, score >70).all()
    if type == 3:
        res = query(id).filter(score <=70).all()
    return __toSet__(res)


def getPlayer(user_id,filter,level):
    if level ==1:
        player_class = [0,1,2]
        prob = [0.01,0.09,0.9]
    else:
        player_class = [0,1]
        prob = [0.02,0.98]
    players = selectPlayer(__randomPick__(player_class, prob))
    player_id = choice(list(players))
    player = query(PlayerBase).get(player_id)
    result = {"name":player.name}
    if player_id not in filter:
        today = datetime.datetime.today()
        duedate = today.replace(year=today.year + 1)
        player = query(PlayerBase).get(player_id)
        contract = '一年%d万，%d年%d月%d日签约，%d年%d月%d日到期' % (player.price, today.year,
                   today.month, today.day, duedate.year, duedate.month, duedate.day)
        add(BagPlayer(user_id, player.id, player.score, player.price, None, duedate, contract))
        print(duedate)
        return (result,State.player)
    else:
        return None


def genTrail(filter):
    player_class = [0,1,2,3]
    prob = [0.3,0.4,0.2,0.1]
    players = selectPlayer(__randomPick__(player_class,prob))
    new_players = players - filter
    if new_players:
        player_id = choice(list(new_players))
    else:
        player_id = choice(list(players))
    time_class = [1,3,5]
    prob = [0.85,0.1,0.05]
    time = __randomPick__(time_class,prob)
    return {"id":player_id,"time":time}


def genPiece():
    player_class = [0,1,2]
    prob = [0.05,0.4,0.55]
    players = selectPlayer(__randomPick__(player_class,prob))
    player_id = choice(list(players))
    num_class = [1,5,10,15]
    prob = [0.45,0.4,0.1,0.05]
    num = __randomPick__(num_class,prob)
    return {"id":player_id,"num":num}
    
def getProp(user_id,filter):
    prop_type = ['trail','piece','fund','exp']
    prob = [0.5,0.3,0.1,0.1]
    ptype = __randomPick__(prop_type, prob)
    if ptype == 'trail':
        res = genTrail(set(filter))
        player = query(PlayerBase).get(res['id'])
        trail_card = query(BagTrailCard).get((user_id,player.id,res['time']))
        if trail_card:
            trail_card.num += 1
        else:
            add(BagTrailCard(user_id,player.id,1,res['time']))
        return ({'name':player.name,'time':res['time']},State.trail)
    if ptype == 'piece':
        res = genPiece()
        player = query(PlayerBase).get(res['id'])
        piece = query(BagPiece).get((user_id,player.id))
        if piece:
            piece.num += res['num']
        else:
            add(BagPiece(user_id,player.id,res['num']))
        return ({'name':player.name,'num':res['num']},State.piece)
    prop = query(BagProp).get(user_id)
    if ptype =='fund':
        if prop:
            prop.fund_card_num += 1
        else:
            add(BagProp(user_id,1,0))
        return ({'card':'fund'},State.fund)
    if ptype =='exp':
        if prop:
            prop.exp_card_num += 1
        else:
            add(BagProp(user_id,0,1))
        return ({'card':'exp'},State.exp)


class OneRecruit(Resource):
    def post(self):
        args = parser.parse_args()
        r_info = query(Recruit).get(args['user_id'])
        u_info = r_info.user
        b_info = [player.player_id for player in u_info.bagplayer]
        delta = (datetime.datetime.now()-r_info.time)
        delta = datetime.timedelta(days=delta.days, seconds=delta.seconds)
        if delta.days > 0 or delta.seconds > 18000:
            r_info.time = datetime.datetime.now()
        else:
            if u_info.money > 100:
                u_info.money -= 100
            else:
                return rMessage(error=State.NoMoney).response
        if r_info.num == 3:
            res = getPlayer(u_info.id,b_info,1)
            if res:
                mes = rMessage(result=res[0],code=res[1])
            else:
                mes = rMessage(error=State.OwnPlayer)
        else:
            res = getProp(u_info.id,b_info)
            mes = rMessage(result=res[0], code=res[1])
        r_info.num = (r_info.num+1)%4
        print(r_info.num)
        try:
            commit()
        except Exception as e:
            rollback()
            print(e)
            mes = rMessage(error=State.FailCommit)
        return mes.response

class FiveRecruie(Resource):
    def post(self):
        args = parser.parse_args()
        u_info = query(User).get(args['user_id'])
        b_info = [player.player_id for player in u_info.bagplayer]
        if u_info.money > 400:
            u_info.money -= 400
        else:
            return rMessage(error=State.NoMoney).response
        res1 = getPlayer(u_info.id,b_info,5)
        if res1:
            mes = rMessage(result=res1[0], code=res1[1])
        else:
            mes = rMessage(error=State.OwnPlayer)
        res2 = getProp(u_info.id,b_info)
        mes.add('prop',res2[0])
        try:
            commit()
        except Exception as e:
            rollback()
            print(e)
            mes = rMessage(error=State.FailCommit)
        return mes.response


recruit_api.add_resource(GetRecruit,'/get_recruit_info')
recruit_api.add_resource(OneRecruit,'/one_recruit')
recruit_api.add_resource(FiveRecruie,'/five_recruit')
# recruit_api.add_resource(RecruitPlayer,'/recruit')
# recruit_api.add_resource(ShowPlayer,'/show_all_payer')

#幸运招募招到已有球员
#已有球员碎片
#piece表为什么需要ID
#trail_card time也应该是主键