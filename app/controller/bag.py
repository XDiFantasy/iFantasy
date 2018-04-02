from flask import Blueprint
from flask_restful import Api, Resource
from app.model import BagPiece,Piece
from app.model import BagPlayer

bag_bp = Blueprint('bag_bp', __name__)
bag_api = Api(bag_bp)


#判断该user是否已经有该piece
def exist_player(user_id,player_id):
    #找到该piece对应的player_id
    one_piece = Piece.query.filter_by(id=player_id).first()
    one_player_id = one_piece.player_id
    #判断背包里是否已经有该player
    data = BagPlayer.query.filter_by(user_id=user_id).all()
    for each in data:
        if one_player_id == each.player_id:
            return True

    return False


class BagPieceApi(Resource):
    def get(self, user_id):
        data = BagPiece.query.filter_by(user_id=user_id).all()
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

    def post(self,user_id,player_id):
        pass

#使用piece合成player,
class UsingPieceApi(Resource):
    def get(self,user_id,player_id):

        #判断该user是否已经有这个player
        exist_flag = exist_player(user_id, player_id)
        if exist_flag:
            return "已拥有"

        data = BagPiece.query.filter_by(user_id=user_id, player_id=player_id).first()

        piece_data = {}
        piece_data['num'] = data.num
        piece_data['total_num'] = data.piece.total_num
        piece_data['name'] = data.piece.player.name

        if piece_data['num'] < piece_data['total_num']:
            return "碎片不足"

        #合成player，从其他地方调用
        #AddBagPlayerApi()

        # 消耗使用掉的piece
        if piece_data['num'] == piece_data['total_num']:
            #delete bag_piece
            #BagPiece.delete.filter_by(user_id,player_id).first()
            #db.session.delete(data)
            pass
        else :
            #修改数据库里的值
            pass

        return "ok"



##
## Setup the Api resource routing here
##
bag_api.add_resource(BagPieceApi,'/piecelist/<int:user_id>/')
bag_api.add_resource(UsingPieceApi,'/usingpiece/<int:user_id>/<int:player_id>')