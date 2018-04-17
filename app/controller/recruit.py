from flask import Blueprint
from flask_restful import Api, Resource, reqparse
from app import db
from app.model import Recruit, User, PlayerBase, BagPlayer, BagTrailCard, BagPiece, BagProp, Theme
from .message import Message
from random import choice, random
import datetime

recruit_bp = Blueprint('recruit_bp', __name__)
recruit_api = Api(recruit_bp)
parser = reqparse.RequestParser()
query = db.session.query
add = db.session.add
commit = db.session.commit
rollback = db.session.rollback
parser.add_argument('user_id', type=int)
parser.add_argument('player_id', type=int)
parser.add_argument('type', type=int)  # 1-score,2-price
parser.add_argument('pos', type=int)  # 0-all,1-c,2-pf,3-sf,4-pg,5-sg
parser.add_argument('theme_id', type=int)
pic_url = "https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/{0}/2017/260x190/{1}.png"


class State:
    ArgError = "arg is incorrect", -250
    NoMoney = "no enough money", -251
    OwnPlayer = "have owned the player", -252  # get piece if the player
    FailCommit = "cannot commit to db", -201


class rMessage(Message):
    def __init__(self, result=None, error=('', 0)):
        if error[1] < 0:
            super(rMessage, self).__init__(result, error[0], error[1])
        else:
            super(rMessage, self).__init__(result)

    def error(self,err):
        self.add('error',err)


class GetRecruit(Resource):
    '''
    fetch recruit num and time to recruit freely
    return {num:num of recruit to get one player,
            time:xx:xx:xx or null if ready to recrresult=uit freely}
    '''

    def get(self):
        args = parser.parse_args()
        user = query(User).get(args['user_id'])
        if user is None:
            return rMessage(error=State.ArgError).response
        info = query(Recruit).get(args['user_id'])
        if info is None:
            info = Recruit(user.id, 0, datetime.datetime.now())
            add(info)
            try:
                commit()
            except Exception as e:
                rollback()
                print(e)
                return rMessage(error=State.FailCommit).response
        delta = (datetime.datetime.now() - info.time)
        delta = datetime.timedelta(days=delta.days, seconds=delta.seconds)
        res = {'num': 3 - info.num}
        if delta.days > 0 or delta.seconds > 18000:
            res['time'] = None
        else:
            res['time'] = (datetime.timedelta(seconds=18000) - delta).seconds
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
        if r < cum: break
    return item

def __commit__(mes):
    try:
        commit()
        return mes
    except Exception as e:
        rollback()
        print(e)
        return rMessage(error=State.FailCommit)

def selectPlayer(type):
    score = PlayerBase.score
    id = PlayerBase.id
    if type == 0:
        res = query(id).filter(score > 90).all()
    if type == 1:
        res = query(id).filter(score <= 90, score > 80).all()
    if type == 2:
        res = query(id).filter(score <= 80, score > 70).all()
    if type == 3:
        res = query(id).filter(score <= 70).all()
    return __toSet__(res)


def addPlayer(user_id, player):
    today = datetime.datetime.today()
    duedate = today.replace(year=today.year + 1)
    contract = '一年%d万，%d年%d月%d日签约，%d年%d月%d日到期' % (player.price, today.year,
                                                  today.month, today.day, duedate.year, duedate.month, duedate.day)
    add(BagPlayer(user_id, player.id, player.score, player.price, duedate, contract))
    pic = pic_url.format(player.team_id, player.id)
    return ({"name": player.name, "pic": pic,"type":"player"}, 0)


def getPlayer(user_id, filter, level):
    if level == 1:
        player_class = [0, 1, 2]
        prob = [0.01, 0.09, 0.9]
    else:
        player_class = [0, 1]
        prob = [0.02, 0.98]
    players = selectPlayer(__randomPick__(player_class, prob))
    player_id = choice(list(players))
    if player_id not in filter:
        player = query(PlayerBase).get(player_id)
        return addPlayer(user_id, player)
    else:
        return (player_id, State.OwnPlayer)


def genTrail(filter):
    player_class = [0, 1, 2, 3]
    prob = [0.3, 0.4, 0.2, 0.1]
    players = selectPlayer(__randomPick__(player_class, prob))
    new_players = players - filter
    if new_players:
        player_id = choice(list(new_players))
    else:
        player_id = choice(list(players))
    time_class = [1, 3, 5]
    prob = [0.85, 0.1, 0.05]
    time = __randomPick__(time_class, prob)
    return {"id": player_id, "time": time}


def genPiece():
    player_class = [0, 1, 2]
    prob = [0.05, 0.4, 0.55]
    players = selectPlayer(__randomPick__(player_class, prob))
    player_id = choice(list(players))
    num_class = [1, 5, 10, 15]
    prob = [0.45, 0.4, 0.1, 0.05]
    num = __randomPick__(num_class, prob)
    return {"id": player_id, "num": num}


def getProp(user_id, filter):
    prop_type = ['trail', 'piece', 'fund', 'exp']
    prob = [0.2, 0.6, 0.1, 0.1]
    ptype = __randomPick__(prop_type, prob)
    if ptype == 'trail':
        res = genTrail(set(filter))
        player = query(PlayerBase).get(res['id'])
        trail_card = query(BagTrailCard).get((user_id, player.id, res['time']))
        if trail_card:
            trail_card.num += 1
        else:
            add(BagTrailCard(user_id, player.id, 1, res['time']))
        pic = pic_url.format(player.team_id, player.id)
        return {'name': player.name, 'time': res['time'], "pic": pic,"type":"trail"}
    if ptype == 'piece':
        res = genPiece()
        player = query(PlayerBase).get(res['id'])
        piece = query(BagPiece).get((user_id, player.id))
        if piece:
            piece.num += res['num']
        else:
            add(BagPiece(user_id, player.id, res['num']))
        pic = pic_url.format(player.team_id, player.id)
        return {'name': player.name, 'num': res['num'], "pic": pic,"type":"piece"}
    prop = query(BagProp).get(user_id)
    if ptype == 'fund':
        if prop:
            prop.fund_card_num += 1
        else:
            add(BagProp(user_id, 1, 0))
        return {'card': 'fund',"type":"fund"}
    if ptype == 'exp':
        if prop:
            prop.exp_card_num += 1
        else:
            add(BagProp(user_id, 0, 1))
        return {'card': 'exp',"type":"exp"}


def toPiece(user_id, player_id):
    player = query(PlayerBase).get(player_id)
    num = player.piece[0].total_num
    piece = query(BagPiece).get((user_id, player.id))
    if piece:
        piece.num += num
    else:
        add(BagPiece(user_id, player.id, num))
    pic = pic_url.format(player.team_id, player.id)
    return ({'name': player.name, 'num': num, "pic": pic,"type":"piece"}, State.OwnPlayer)


class OneRecruit(Resource):
    def post(self):
        args = parser.parse_args()
        r_info = query(Recruit).get(args['user_id'])
        if r_info is None:
            return rMessage(error=State.ArgError).response
        u_info = r_info.user
        b_info = [player.player_id for player in u_info.bagplayer]
        delta = (datetime.datetime.now() - r_info.time)
        delta = datetime.timedelta(days=delta.days, seconds=delta.seconds)
        if delta.days > 0 or delta.seconds > 18000:
            r_info.time = datetime.datetime.now()
        else:
            if u_info.money >= 100:
                u_info.money -= 100
            else:
                return rMessage(error=State.NoMoney).response
        if r_info.num == 2:
            res = getPlayer(u_info.id, b_info, 1)
            if res[1] == State.OwnPlayer:
                res = toPiece(u_info.id, res[0])
                mes = rMessage(res[0], res[1])    ####
            else:
                mes = rMessage(res[0])          ####
        else:
            res = getProp(u_info.id, b_info)
            mes = rMessage(res)      ####
        r_info.num = (r_info.num + 1) % 3
        mes = __commit__(mes)
        return mes.response


class FiveRecruie(Resource):
    def post(self):
        args = parser.parse_args()
        u_info = query(User).get(args['user_id'])
        if u_info is None:
            return rMessage(error=State.ArgError).response
        b_info = [player.player_id for player in u_info.bagplayer]
        if u_info.money >= 400:
            u_info.money -= 400
        else:
            return rMessage(error=State.NoMoney).response  # no money
        res = getPlayer(u_info.id, b_info, 5)
        items=list()
        isPiece = False
        if res[1] == State.OwnPlayer:
            res = toPiece(u_info.id, res[0])
            isPiece = True
        items.append(res[0])
        for i in range(4):
            items.append(getProp(u_info.id, b_info))
        if isPiece :
            mes = rMessage(items,State.OwnPlayer)       ####
        else:
            mes = rMessage(items)  ####
        mes = __commit__(mes)
        return mes.response


class RecruitPlayer(Resource):
    def post(self):
        args = parser.parse_args()
        user = query(User).get(args['user_id'])
        player = query(PlayerBase).get(args['player_id'])
        if (user is None) or (player is None):
            return rMessage(error=State.ArgError).response
        if user.money < player.price:
            return rMessage(error=State.NoMoney).response
        player_ids = [player.player_id for player in user.bagplayer]
        if player.id in player_ids:
            return rMessage(error=State.OwnPlayer).response
        user.money -= player.price
        res = addPlayer(user.id, player)
        mes = __commit__(rMessage(res[0]))   ####
        return mes.response


def dataFilter(items, strs):
    if strs:
        items = items.filter(db.or_(PlayerBase.pos1 == strs, PlayerBase.pos2 == strs))
    res = list()
    for item in items.all():
        pic = pic_url.format(item.team_id, item.id)
        res.append({"id": item.id, "name": item.name, "pos1": item.pos1, "pos2": item.pos2, "price": item.price,
                    "score": item.score, "pic": pic})
    return res


class ShowPlayer(Resource):
    def get(self):
        index = parser.parse_args()['type']
        pos = parser.parse_args()['pos']
        if not index:
            index = 0
        if not pos:
            pos = 0
        if index not in [0, 1, 2]:
            return rMessage(error=State.ArgError).response
        order = [PlayerBase.id, PlayerBase.score, PlayerBase.price]
        data = query(PlayerBase).order_by(db.desc(order[index]))
        if pos == 0:
            return rMessage(dataFilter(data, None)).response
        if pos == 1:
            return rMessage(dataFilter(data, 'c')).response
        if pos == 2 or pos == 3:
            return rMessage(dataFilter(data, 'f')).response
        if pos == 4 or pos == 5:
            return rMessage(dataFilter(data, 'g')).response


class BuyTheme(Resource):
    def post(self):
        args = parser.parse_args()
        theme = query(Theme).get(args['theme_id'])
        user = query(User).get(args['user_id'])
        if (user is None) or (theme is None):
            return rMessage(error=State.ArgError).response
        if user.money < theme.price:
            return rMessage(error=State.NoMoney).response
        user.money -= theme.price
        bag_players = [player.player_id for player in user.bagplayer]
        res = list()
        for player_id in [theme.player_one_id, theme.player_two_id, theme.player_three_id]:
            if player_id in bag_players:
                data = toPiece(user.id, player_id)
            else:
                player = query(PlayerBase).get(player_id)
                data = addPlayer(user.id, player)
                data[0]['num'] = 0
            res.append(data[0])
        mes = __commit__(rMessage(res))       ####
        return mes.response


recruit_api.add_resource(GetRecruit, '/get_recruit_info')
recruit_api.add_resource(OneRecruit, '/one_recruit')
recruit_api.add_resource(FiveRecruie, '/five_recruit')
recruit_api.add_resource(RecruitPlayer, '/recruit')
recruit_api.add_resource(ShowPlayer, '/show_all_payer')
recruit_api.add_resource(BuyTheme, '/buy_theme')
