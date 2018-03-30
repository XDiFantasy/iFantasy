from flask import Blueprint
from flask_restful import Api, Resource
from app.model import BagPiece

bag_bp = Blueprint('bag_bp', __name__)
bag_api = Api(bag_bp)



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

class UsingPieceApi(Resource):
    def get(self,user_id,piece_id):

        #exist_flag = exist_player(user.id, piece.id)
        #if exist_flag
        #    return "已拥有 %r" %piece_data['name']

        data = BagPiece.query.filter_by(user_id=user_id, piece_id=piece_id).first()
        result = []

        piece_data = {}
        piece_data['num'] = data.num
        piece_data['total_num'] = data.piece.total_num
        piece_data['name'] = data.piece.player.name

        if piece_data['num'] < piece_data['total_num']:
            return "碎片不足"

        piece_data['user_id'] = user_id
        piece_data['player_id'] = player_id
        piece_data['score'] = data.piece.player.score
        piece_data['salary'] = 200


        return "ok"

##
## Setup the Api resource routing here
##
bag_api.add_resource(BagPieceApi,'/pieces/<int:user_id>/')
bag_api.add_resource(UsingPieceApi,'/usingpiece/<int:user_id>/<int:piece_id>')