from flask import Blueprint, jsonify, request
from flask_restful import Api, Resource,reqparse
from app.model import User, UserGame
from app import db
import threading
import time
from .errors import GameError
from .message import Message
from collections import defaultdict
from .user import UserError,Auth

class GameError:
    GAME_FAILED = 'game failed', -1
    RESULT_SENDED = 'result sended', -2
class GameMessage(Message):
    GAMEING = 'Gaming'
    MATCHING = 'Matching'
    DONE = 'Done'

    def __init__(self,result = None, error='', state=0):
        super(GameMessage,self).__init__(result,error,state)
    @property
    def gaming(self):
        self.add(result,self.GAMEING)
        return self
    @property
    def matching(self):
        self.add(result,self.MATCHING)
        return self
    



game_bp = Blueprint('game_bp', __name__, static_folder="../static/game")
game_api = Api(game_bp)
session = db.session

users = defaultdict(list)
results = {}
# gaming matching done none
user_states = defaultdict(lambda : None)

users_lock = threading.Lock()
results_lock = threading.Lock()

    
def rank(user):
    return 1

def gaming(user1, user2):
    global results, results_lock
    
    results_lock.acquire()
    results[str(user1)] = {'score':20}
    results[str(user2)] = {'socre':30}

    results_lock.release()
    user_states[str(user1)] = GameMessage.DONE
    user_states[str(user2)] = GameMessage.DONE
    pass
    
def match(user_rank):
    global users, users_lock
    if len(users[user_rank]) != 0:
        users_lock.acqurie()
        ouser = users[user_rank].pop()
        users_lock.release()
        return ouser
    return None
        


class Game(Resource):
    
    parse = reqparse.RequestParser()
    parse.add_argument('user_id', type=int)

    def post(self):
        global users, users_lock
        args = self.parse.parse_args(strict=True)

        token = request.headers.get('Authorization')
        user_id = args['user_id']

        if Auth.authToken(user_id, token):
            return str(GameMessage(None,*UserError.AUTH_FAILED))

        user = User.query.filter_by(id = user_id).first()
        if not user:
            return str(GameMessage(None, *UserError.ILLEGAL_USER))
        user_states[str(user)] = GameMessage.MATCHING
        user_rank = rank(user)
        
        ouser = match(user_rank)
        if ouser is None:
            #take user into users
            users_lock.acquire()
            users[user_rank].append(user)
            users_lock.release()
            return str(GameMessage().matching)
        gameThread = threading.Thread(target=gaming, args=(user,ouser))
        gameThread.start()
        user_states[str(user)] = GameMessage.GAMING
        return str(GameMessage().gaming)

class GameResult(Resource):
    
    def get(self, user_id):
        global results, results_lock
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return str(GameMessage(None, *GameError.ILLEGAL_USER))
        if str(user) in results:
            results_lock.acquire()
            res = results[str(user)]
            del results[str(user)]

            results_lock.release()
            user_states[str(user)] = GameMessage.DONE
            return str(GameMessage(result=res))
        if user_states[str(user)] == GameMessage.GAMING:
            return str(GameMessage().gaming)
        if user_states[str(user)] == GameMessage.MATCHING:
            return str(GameMessage().matching)
        if user_states[str(user)] == GameMessage.DONE:
            #may be a error : 先发一个error，如果客户端继续请求结果，则从数据库中返回
            reuslt = UserGame.query.filter_by(user_id=user_id).order_by(UserGame.time.desc()).first()
            if not result:
                return str(GameMessage())
            return str(GameMessage(result,*GameError.RESULT_SENDED))

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
        
        
        

game_api.add_resource(Game,'/game')
game_api.add_resource(GameResult, '/gameresult/<int:user_id>')
        


        
