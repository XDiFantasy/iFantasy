from flask import Blueprint, jsonify
from flask_restful import Api, Resource,reqparse
from app.model import User
from app import db
from .utils import userAuth
import threading
import time


game_bp = Blueprint('game_bp', __name__, static_folder="../static/game")
game_api = Api(game_bp)
session = db.session

users = []
results = {}

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

    pass
    
        

class Game(Resource):
    
    parse = reqparse.RequestParser()
    parse.add_argument('user_id', type=int)
    parse.add_argument('token',type=str)

    def post(self):
        '''
        {
            user_id:int,
            token:string,
        }
        '''
        global users, users_lock
        args = self.parse.parse_args(strict=True)
        # user auth
        token = args['token']
        user_id = args['user_id']
        #auth function call
        res = userAuth(user_id, token)
        if not res:
            return jsonify({'error':"auth fail"})
        user = User.query.filter_by(id = user_id).first()
        if not user:
            return jsonify({'error':"no such user"})
        for ouser in users:
            if  rank(user) == rank(ouser):
                # add the two in game thread
                users_lock.acquire()
                threading.Thread(target=gaming, args=(user, ouser)).start()
                
                users.remove(ouser)
                users_lock.release()
                return jsonify({'message':"gaming"})
        #no same rank , add in users
        users_lock.acquire()
        users.append(user)
        users_lock.release()
        return jsonify({"message":"picking"})

class GameResult(Resource):
    
    def get(self, user_id):
        global results, results_lock
        print(results)
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return jsonify({"error":"no such user"})
        if str(user) in results:
            results_lock.acquire()

            res = results[str(user)]
            del results[str(user)]

            results_lock.release()
            return jsonify(res)
        return jsonify({"message":"gaming"})

class FriendGame(Resource):
    
    parse = reqparse.RequestParser()
    parse.add_argument("user_id", type=int)
    parse.add_argument('firend_id',type=int)
    
    def post(self):
        args = parse.parse_args()
        user_id = args['user_id']
        friend_id = args['user_id']
        user = User.query.filter_by(id=user_id).first()
        firend = User.query.filter_by(id=friend_id).first()
        if not user or not friend:
            return jsonify({"error":'no such user'})
        
        

game_api.add_resource(Game,'/game')
game_api.add_resource(GameResult, '/gameresult/<int:user_id>')
        


        
