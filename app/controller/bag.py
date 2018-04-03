from flask import Blueprint
from flask_restful import Api, Resource
from app.model import BagPiece,Piece
from app.model import BagPlayer
from app.controller import Message
#不需要么？？from datetime import datetime

bag_bp = Blueprint('bag_bp', __name__)
bag_api = Api(bag_bp)

class BagError:
    BAG_EMPTY = 'Your bag is empty',  -1
    BAG_FULL = 'Your bag is full', -2
    BAG_REPEAT = 'you already have', -3

class BagMessage(Message):
    
    def __init__(self,result = None, error='', state=0):
        super(BagMessage,self).__init__(result, error, state)

#列出背包里的piece
class BagPieceApi(Resource):
    def get(self, user_id):
        data = BagPiece.query.filter_by(user_id=user_id).all()
        if data == None :
            return BagMessage(None, BAG_EMPTY).response

        result = []
        for each in data:
            each_data = {}
            each_data['name'] = each.piece.player.name
            each_data['num'] = each.num
            each_data['total'] = each.piece.total_num
            each_data['pos1'] = each.piece.player.pos1
            each_data['pos2'] = each.piece.player.pos2

            result.append(each_data)

        return {'data':result}


#使用piece合成player,
#合成player接口暂无
class UsingPieceApi(Resource):
    def post(self,user_id,player_id):
        # 判断该user是否已经有这个player
        if BagPlayer.query.filter_by(user_id=user_id,player_id=player_id).first() != None :
            return "已拥有"

        data = BagPiece.query.filter_by(user_id=user_id, player_id=player_id).first()

        piece_data = {}
        piece_data['num'] = data.num
        piece_data['total_num'] = data.piece.total_num
        piece_data['name'] = data.piece.player.name

        if piece_data['num'] < piece_data['total_num']:
            return "碎片不足"

        # 合成player，从其他地方调用
        # AddBagPlayerApi()

        # 消耗使用的piece
        if piece_data['num'] == piece_data['total_num']:
            db.session.delete(data)
            #BagPiece.query.filter_by(user_id=user_id, player_id=player_id).delete()
            db.session.commit()
        else:
            new_num = piece_data['num'] - piece_data['total_num']
            data.update({'num':new_num})
            db.session.commit()

        return "ok"

#列出背包里的体验卡
class BagTrailCardApi(Resource):
    def get(self,user_id):
        data = BagTrailCard.query.filter_by(user_id=user_id).all()
        if data == None:
            return {'data':'背包无体验卡'}

        result = []
        for each in data:
            each_data = {}
            each_data['name'] = each.player.name
            each_data['num'] = each.num
            each_data['time'] = each.time
            each_data['pos1'] = each.player.pos1
            each_data['pos2'] = each.player.pos2

            result.append(each_data)
        return {'data':result}


class UsingTrailCardApi(Resource):
    def post(self,user_id,player_id,time):
        playerdata = BagPlayer.query.filter_by(user_id=user_id,player_id=player_id).first()

        #若已有player,怎修改duetime增加签约时间
        if playerdata != None:
            timedata = playerdata.duetime
            timedata += timedelta(time)
            db.session.commit()
            return "增加duetime"
        #若没有player,则增加一个球员。
        else:
            #addPlayer接口
            #return '增加player'
            pass

#列出背包里的装备
#目前还没有设计具体装备，只留个接口
class BagEquipApi(Resource):
    def get(self,user_id):
        data = BagEquip.query.filter_by(user_id).all()
        if data == None:
            return {'data':'背包无装备'}

        return {'data':'装备未定义'}


##
## Setup the Api resource routing here
##
bag_api.add_resource(BagPieceApi,'/piecelist/<int:user_id>/')
bag_api.add_resource(UsingPieceApi,'/usingpiece/<int:user_id>/<int:player_id>')
bag_api.add_resource(BagTrailCardApi,'/trailcardlist/<int:user_id>')
bag_api.add_resource(UsingTrailCardApi,'/usingtrailcard/<int:user_id>/<int:player_id>')
bag_api.add_resource(BagEquipApi,'/equiplist/<int:user_id>')