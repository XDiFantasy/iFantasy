from flask import Blueprint, jsonify, request
from flask_restful import Api, Resource,reqparse
from app.model import User, UserGame
from app import db
import threading
import time
from .message import Message
from collections import defaultdict
from .user import UserError,Auth

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


results = {}
# gaming matching done none
user_states = defaultdict(lambda : None)

users_lock = threading.Lock()
results_lock = threading.Lock()

matchers = []
    
def rank(user):
    return 1

def gaming(user1, user2):
    global results, results_lock
    #net
    results_lock.acquire()
    results[str(user1)] = GameResult()
    results[str(user2)] = GameResult()
    results_lock.release()
    user_states[str(user1)] = GameMessage.DONE
    user_states[str(user2)] = GameMessage.DONE
    pass

def match(user_rank, range_ = 0):
    global users, users_lock
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
    def __init__(self,user,time):
        self.__rank = rank(user)
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
        global users, users_lock
        args = self.parse.parse_args(strict=True)

        token = request.headers.get('Authorization')
        user_id = args['user_id']

        if Auth.authToken(user_id, token):
            return GameMessage(None,*UserError.AUTH_FAILED).response

        user = User.query.filter_by(id = user_id).first()
        if not user:
            return GameMessage(None, *UserError.ILLEGAL_USER).response
        user_states[user_id] = GameMessage.MATCHING
        user_rank = rank(user)
        
        ouser_id = match(user_rank)
        if ouser_id is None:
            #take user into users
            users_lock.acquire()
            users[user_rank].append(user)
            users_lock.release()
            return GameMessage().matching.response
        gameThread = threading.Thread(target=gaming, args=(user,ouser))
        user_states[str(user)] = GameMessage.GAMING
        user_states[str(ouser)] = GameMessage.GAMING
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
        


        
