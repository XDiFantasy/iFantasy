from flask import Blueprint, jsonify, request
from flask_restful import Api, Resource,reqparse
from app.model import User, UserGame
from app.model.game import UserMatch
from app import db
import threading
import time
from .message import Message
from collections import defaultdict
from .user import UserError,Auth
from math import pow, log10

game_bp = Blueprint('game_bp', __name__, static_folder="../static/game")
game_api = Api(game_bp)


class GameError:
    GAME_FAILED = 'game failed', -701
    RESULT_SENDED = 'result sended', -702
    NO_RESULT = 'no result', -703

class GameMessage(Message):
    GAMING = 'Gaming'
    MATCHING = 'Matching'
    DONE = 'Done'

    def __init__(self,result = None, error='', state=0):
        super(GameMessage,self).__init__(result,error,state)
    @property
    def gaming(self):
        self.add('result',self.GAMING)
        return self
    @property
    def matching(self):
        self.add('result',self.MATCHING)
        return self

class GameResult:
    
    def __init__(self,pts=0,oreb=0,dreb=0,ast=0,stl=0,blk=0,in_pts=0,tov=0,ft=0,three_pt=0):
        self.__result = dict(
            {'pts':pts, 'oreb':oreb,'dreb':dreb,'ast':ast,'stl':stl,
            'blk':blk,'in_pts':in_pts, 'tov':tov,'ft':ft,'3pt':three_pt}
        )
    @property
    def result(self):
        return self.__result

class GlobalVar:
    matcher_lock = threading.Lock()
    results_lock = threading.Lock()
    userstate_lock = threading.Lock()
    
    def __init__(self):
        self.results = {}
        self.matchers = defaultdict(list)
        self.userStates = defaultdict(lambda : None)

globalVar = GlobalVar()
p = 0.618
k = 400*log10(p/(1-p))/5*2
d = 1000
    
def rank(user):
    return (user.usermatch.score - d) // k

def ELO(ra, rb, sa,k = k):
    ea = 1/(1+pow(10,-(ra-rb)/400))
    eb = 1-ea
    new_ra = ra + k*(sa-ea)
    new_rb = rb + k*(1-sa-eb)
    return new_ra, new_rb
    

def gaming(user1, user2):
    global globalVar
    #net game
    globalVar.results_lock.acquire()
    globalVar.results[str(user1)] = GameResult()
    globalVar.results[str(user2)] = GameResult()
    globalVar.results_lock.release()
    globalVar.userstate_lock.acquire()
    globalVar.userStates[str(user1)] = GameMessage.DONE
    globalVar.userStates[str(user2)] = GameMessage.DONE
    globalVar.userstate_lock.release()
    pass

def match(user_rank, range_ = 0):
    global globalVar
    for rank in range(max(user_rank-range_,MIN_RANK),min(user_rank+range_,MAX_RANK)):
        if len(users[rank]) != 0:
            users_lock.acquire()
            ouser = users[user_rank].pop()
            users_lock.release()
            return ouser.id
    return None

class Matcher:
    MIN_RANK = 0
    MAX_RANK = 10
    def __init__(self,user,rank,time):
        self.__rank = rank
        self.__time = time
        self.__user = user

    def __getRange(self):
        currTime = time.time()
        due = int(currTime - self.__time) // 10
        return max(self.__rank-due, self.MIN_RANK) , min(self.__rank+due, self.MAX_RANK)
    def can(self, rank):
        range = self.__getRange()
        return rank >= range[0] and rank  <= range[1]
    @property
    def rank(self):
        return self.__rank
    


class Game(Resource):
    
    parse = reqparse.RequestParser()
    parse.add_argument('user_id', type=int)

    def post(self):
        global globalVar
        args = self.parse.parse_args(strict=True)

        user_id = args['user_id']

        user = User.query.filter_by(id = user_id).first()
        if not user:
            return GameMessage(None, *UserError.ILLEGAL_USER).response
        globalVar.userstate_lock.acquire()
        globalVar.userStates[user_id] = GameMessage.MATCHING
        globalVar.userstate_lock.release()
        user_rank = rank(user)
        
        ouser_id = match(user_rank)
        if ouser_id is None:
            #take user into matchers
            globalVar.matcher_lock.acquire()
            globalVar.matchers.append(user)
            globalVar.matcher_lock.release()
            return GameMessage().matching.response
        ouser = User.query.filter_by(id=ouser_id).first()
        if ouser is None:
            return GameMessage(None, *UserError.ILLEGAL_USER).response
        gameThread = threading.Thread(target=gaming, args=(user,ouser))
        globalVar.userstate_lock.acquire()
        globalVar.userStates[str(user)] = GameMessage.GAMING
        globalVar.userStates[str(ouser)] = GameMessage.GAMING
        globalVar.userstate_lock.release()
        gameThread.start()
        return GameMessage().gaming.response

class GameResult(Resource):
    
    def get(self, user_id):
        global results, results_lock
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return GameMessage(None, *UserError.ILLEGAL_USER).response
        if str(user) in results:
            results_lock.acquire()
            res = results[str(user)]
            del results[str(user)]

            results_lock.release()
            user_states[str(user)] = GameMessage.DONE
            return GameMessage(result=res,state=700).response
        if user_states[str(user)] == GameMessage.GAMING:
            return GameMessage(state=700).gaming.response
        if user_states[str(user)] == GameMessage.MATCHING:
            #change rank

            return GameMessage(state=700).matching.response
        if user_states[str(user)] == GameMessage.DONE:
            #may be a error : 先发一个error，如果客户端继续请求结果，则从数据库中返回
            result = UserGame.query.filter_by(user_id=user_id).order_by(UserGame.time.desc()).first()
            if not result:
                return GameMessage(None,*GameError.NO_RESULT).response
            return GameMessage(result,*GameError.RESULT_SENDED).response

class FriendGame(Resource):
    
    parse = reqparse.RequestParser()
    parse.add_argument("user_id", type=int)
    parse.add_argument('firend_id',type=int)
    
    def post(self):
        args = self.parse.parse_args()
        user_id = args['user_id']
        friend_id = args['user_id']
        user = User.query.filter_by(id=user_id).first()
        firend = User.query.filter_by(id=friend_id).first()
        if not user or not friend:
            return jsonify({"error":'no such user'})
        return firend
        
        
        

game_api.add_resource(Game,'/game')
game_api.add_resource(GameResult, '/gameresult/<int:user_id>')
        


        
