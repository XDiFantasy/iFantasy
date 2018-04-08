from flask import Blueprint, jsonify, request
from flask_restful import Api, Resource,reqparse
from app.model import User, UserGame, LineUp, BagPlayer, UserMatch, InputData, Strategy
from app import db
import threading
import time
from .message import Message
from collections import defaultdict
from .user import UserError,Auth
from math import pow, log10
from queue import Queue
import datetime

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
    ERROR = 'Error'
    MATCHED = 'Matched'

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
            'blk':blk,'in_pts':in_pts, 'tov':tov,'ft':ft,'three_pt':three_pt}
        )
    @property
    def result(self):
        return self.__result

class Rank:
    p = 0.618
    k = 400*log10(p/(1-p))/5*2
    d = 1000
    def __init__(self):
        # scores = db.session.query(UserMatch.user_id, UserMatch.score).all()
        # self.scores = {row[0]:row[1] for row in scores}
        self.scores = {}
    @staticmethod
    def ELO( ra, rb, sa):
        ea = 1/(1+pow(10,-(ra-rb)/400))
        eb = 1-ea
        new_ra = ra + Rank.k*(sa-ea)
        new_rb = rb + Rank.k*(1-sa-eb)
        return new_ra, new_rb
    def __rank(self, score):
        r = (score - self.d) // self.k
        return r if r >= 0 else 0
    def __call__(self,user):
        userMatch = UserMatch.query.filter_by(user_id = user.id).first()
        self.scores[user.id] = userMatch.score
        return self.__rank(self.scores[user.id])
    
    def update(self, user,new_score):
        userMatch = UserMatch.query.filter_by(user_id=user.id).first()
        userMatch.score = new_score
        db.session.add(userMatch)
        db.session.commit()
        self.scores[user.id] = new_score  

class GlobalVar:
    results = {}
    matchers = defaultdict(lambda : Queue(-1))
    userStates = defaultdict(lambda : None)
    tasks = Queue(-1)
    lineups = {}
    rank = Rank()
    gameRooms = {}

class GameInputData:
    __colNames = (
        'pts', 'fg_pct','three_pt_pct', 'fta', 'oreb_pct',
        'dreb_pct', 'ast_pct', 'tov', 'stl','blk','pf','p_m'
    )
    def __init__(self, input_data):
        self.__result = {
            colName : getattr(input_data,colName) for colName in self.__colNames
        }
def net(players):
    '''
        players : [[user1's players],[user2's players]]
    '''
    return GameResult(), GameResult()

    

class GameThread(threading.Thread):
    def __init__(self, matcher1, matcher2):
        threading.Thread.__init__(self)
        self.matcher1 = matcher1
        self.matcher2 = matcher2
    def processInputData(self):
        for lineup in [self.lineup1, self.lineup2]:
            strategy = Strategy.query.get(lineup.strategy_id)
            for player,pos in zip([lineup.sf, lineup.sg, lineup.c, lineup.pf, lineup.pg],
                ['sf','sg','c','pf','pg']):
                pass


    def mainGame(self):
        '''
        net : 
    '''
        def getInputData(playerId):
            player = BagPlayer.query.filter_by(id=playerId).first()
            input_data = InputData.query.filter_by(id=player.id).first()
            return GameInputData(input_data)
        def finalPlayers():
            raw_players = [[getInputData(lineup.sf), getInputData(lineup.pf), 
            getInputData(lineup.c), getInputData(lineup.pg), getInputData(lineup.sg)] 
        players = 
            for lineup in [lineup1,lineup2] ]
        player1Res, player2Res = net(players)
        return player1Res, player2Res
    def getLineups(self):
        matcher1 = self.matcher1
        matcher2 = self.matcher2
        lineup1 = LineUp.query.filter_by(id=GlobalVar.lineups[str(matcher1)]).first()
        lineup2 = LineUp.query.filter_by(id=GlobalVar.lineups[str(matcher2)]).first()
        if not lineup1 and not lineup2:
            GlobalVar.tasks.put(ModifyStateTask(str(matcher1),GameMessage.ERROR))
            GlobalVar.tasks.put(ModifyStateTask(str(matcher1),GameMessage.ERROR))
            return None
        if not lineup1 and lineup2:
            GlobalVar.tasks.put(ModifyStateTask(str(matcher1),GameMessage.ERROR))
            GlobalVar.tasks.put(AddInMatchersTask(matcher2.user))
            GlobalVar.tasks.put(ModifyStateTask(str(matcher2),GameMessage.MATCHING))
            return None
        if not lineup2 and lineup1:
            GlobalVar.tasks.put(ModifyStateTask(str(matcher2),GameMessage.ERROR))
            GlobalVar.tasks.put(AddInMatchersTask(matcher1.user))
            GlobalVar.tasks.put(ModifyStateTask(str(matcher1),GameMessage.MATCHING))
            return None
        self.lineup1 = lineup1
        self.lineup2 = lineup2
    def writeResult(self, player1Res, player2Res):
        matcher1 = self.matcher1
        matcher2 = self.matcher2
        sa = 1 if player1Res.result['pts'] > player2Res.result['pts'] else 0.5 if player1Res.result['pts'] == player2Res.result['pts'] else 0
        new_score1, new_score2 = GlobalVar.rank.ELO(matcher1.rank,matcher2.rank,sa)
        GlobalVar.tasks.put(UpdateScoreTask(matcher1.user,new_score1))
        GlobalVar.tasks.put(UpdateScoreTask(matcher2.user,new_score2))
        userGame1 = UserGame(matcher1.user.id, datetime.datetime.today(),**(player1Res.result))
        userGame2 = UserGame(matcher1.user.id, datetime.datetime.today(),**player2Res.result)
        db.session.add(userGame1)
        db.session.add(userGame2)
        db.session.commit()
        GlobalVar.tasks.put(AddInResultsTask(str(matcher1),player1Res))
        GlobalVar.tasks.put(AddInResultsTask(str(matcher2),player2Res))
        
        GlobalVar.tasks.put(ModifyStateTask(str(matcher1),GameMessage.DONE))
        GlobalVar.tasks.put(ModifyStateTask(str(matcher2),GameMessage.DONE))
    def run(self):
        lineups = self.getLineups()
        if lineups is not None:
            player1Res, player2Res = mainGame(*lineups)
            self.writeResult(player1Res, player2Res)
        
  

class ProcessTasksThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        global GlobalVar
        while True:
            task = GlobalVar.tasks.get()
            task.run()
            GlobalVar.tasks.task_done()

class MatchThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        global GlobalVar
        while True:
            for _, matchers in GlobalVar.matchers.items():
                start_time = time.time()
                if matchers.qsize() >= 2:
                    while matchers.qsize() > 1 and time.time() - start_time < 2:
                        matcher1 = matchers.get()
                        matchers.task_done()
                        matcher2 = matchers.get()
                        matchers.task_done()
                        GlobalVar.tasks.put(AddInGameRoomTask(matcher1, matcher2))
                        GlobalVar.tasks.put(ModifyStateTask(str(matcher1),GameMessage.GAMING))
                        GlobalVar.tasks.put(ModifyStateTask(str(matcher2),GameMessage.GAMING))
                        GlobalVar.tasks.put(GameTask(matcher1,matcher2))
            time.sleep(2)

class Matcher:
    MIN_RANK = 0
    MAX_RANK = 10
    def __init__(self,user):
        self.__rank = GlobalVar.rank(user)
        self.__time = time.time()
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
    def __str__(self):
        return str(self.__user)
    @property
    def user(self):
        return self.__user
        
class Task:
    def __init__(self):
        pass
    def run(self):
        pass

class ModifyStateTask(Task):
    
    def __init__(self, user_str, new_state):
        self.user_str = user_str
        self.state = new_state
    def run(self):
        GlobalVar.userStates[self.user_str] = self.state
class AddInResultsTask(Task):
    def __init__(self,user_str, game_result):
        self.user_str = user_str
        self.game_result = game_result
    def run(self):
        GlobalVar.results[self.user_str] = self.game_result
class AddInMatchersTask(Task):
    def __init__(self, user):
        self.user = user
    def run(self):
        matcher = Matcher(self.user)
        GlobalVar.matchers[matcher.rank].put(matcher)   #[matcher.rank].append(matcher)
class GameTask(Task):
    def __init__(self,matcher1, matcher2):
        self.matcher1 = matcher1
        self.matcher2 = matcher2
    def run(self):
        gameThread = GameThread(self.matcher1, self.matcher2)
        gameThread.start()
class ModifyLineupTask(Task):
    def __init__(self, user_str, lineup_id):
        self.user_str = user_str
        self.lineup_id = lineup_id
    def run(self):
        GlobalVar.lineups[self.user_str] = self.lineup_id

class UpdateScoreTask(Task):
    def __init__(self,user, new_score):
        self.user = user
        self.new_score = new_score    
    def run(self):
        GlobalVar.rank.update(self.user, self.new_score)
class DelResultTask(Task):
    def __init__(self, user):
        self.user = user
    def run(self):
        del GlobalVar.results[str(self.user)]    
class AddInGameRoomTask(Task):
    def __init__(self, matcher1, matcher2):
        self.matcher1 = matcher1
        self.matcher2 = matcher2
    def run(self):
        GlobalVar.gameRooms[str(self.matcher1)] = self.matcher2
        GlobalVar.gameRooms[str(self.matcher2)] = self.matcher1
class DelGameRoomTask(Task):
    def __init__(self, matcher1, matcher2):
        self.matcher1 = matcher1
        self.matcher2 = matcher2
    def run(self):
        del GlobalVar.gameRooms[str(self.matcher1)]
        del GlobalVar.gameRooms[str(self.matcher2)]


class GameApi(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('user_id',type=int)
    parser.add_argument('lineup_id',type=int)
    def post(self):
        global GlobalVar
        args = self.parser.parse_args(strict=True)
        user_id = args['user_id']
        lineup_id = args['lineup_id']

        user = User.query.filter_by(id=user_id).first()
        if not user:
            return GameMessage(None,*UserError.ILLEGAL_USER).response
        userState = GlobalVar.userStates[str(user)]
        if userState is None or userState == GameMessage.DONE:
            GlobalVar.tasks.put(ModifyStateTask(str(user),GameMessage.MATCHING))
            GlobalVar.tasks.put(ModifyLineupTask(str(user),lineup_id))
            GlobalVar.tasks.put(AddInMatchersTask(user))
            return GameMessage().matching.response
        return GameMessage(None, *GameError.NO_RESULT)
        
        

class GameResultApi(Resource):

    def get(self,user_id):
        global GlobalVar
        print(GlobalVar.userStates)
        print(GlobalVar.results)
        print(GlobalVar.matchers)
        user = User.query.filter_by(id = user_id).first()
        if not user:
            return GameMessage(None,*UserError.ILLEGAL_USER).response
        if str(user) not in GlobalVar.results:
            userState = GlobalVar.userStates[str(user)]
            if userState is None:
                return GameMessage(None, *GameError.GAME_FAILED).response
            elif userState == GameMessage.GAMING:
                
                return GameMessage(GameMessage.GAMING,state=700).response
            elif userState == GameMessage.MATCHING:
                return GameMessage(GameMessage.MATCHING,state=700).response
            elif userState == GameMessage.DONE:
                return GameMessage(None, *GameError.RESULT_SENDED).response
            else:
                return GameMessage(None, *GameError.GAME_FAILED).response

        gameResult = GlobalVar.results[str(user)]
        db.session.add(UserGame(user_id, datetime.datetime.now(), **gameResult.result))
        db.session.commit()
        matcher2 = GlobalVar.gameRooms[str(user)]
        matcher1 = GlobalVar.gameRooms[str(matcher2)]
        GlobalVar.tasks.put(DelGameRoomTask(matcher1, matcher2))
        return  GameMessage(gameResult.result,state=700).response
    def delete(self, user_id):
        global GlobalVar
        user = User.query.filter_by(id = user_id).first()
        if not user:
            return GameMessage(None,*UserError.ILLEGAL_USER).response
        GlobalVar.tasks.put(DelResultTask(user))
        GlobalVar.tasks.put(ModifyStateTask(str(user),GameMessage.DONE))
        return GameMessage(state=700).response

class GameMatchedApi(Resource):
    def get(self, user_id):
        user = User.query.filter_by(id = user_id).first()
        if not user:
            return GameMessage(None,*UserError.ILLEGAL_USER).response
        user_state = GlobalVar.userStates[str(user)]
        if user_state == GameMessage.GAMING or \
            user_state == GameMessage.DONE:
            #返回LineUp信息
            other = GlobalVar.gameRooms[str(user)]
            return GameMessage('other linup',state=700).response
        return GameMessage(GameMessage.MATCHING,state=700).response


       
game_api.add_resource(GameApi,'/game')
game_api.add_resource(GameResultApi,'/game_result/<int:user_id>')
game_api.add_resource(GameMatchedApi,'/game_matched/<int:user_id>')

matchThread = MatchThread()
matchThread.setDaemon(True)
processTaskThread = ProcessTasksThread()
processTaskThread.setDaemon(True)

matchThread.start()
processTaskThread.start()


        
