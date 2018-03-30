from flask import Blueprint
from flask_restful import Api, Resource
from app.model import BagPiece
from operator import attrgetter  #sort

bag_bp = Blueprint('bag_bp', __name__)
bag_api = Api(bag_bp)


class BagPieceApi(Resource):
    def get(self, user_id):
        data = BagPiece.query.filter_by(user_id=user_id).all()
        result = []
        for piece in data:
            piece_data = {}
            piece_data['name'] = piece.piece.player.name
            piece_data['num'] = piece.num
            piece_data['total'] = piece.piece.total_num
            piece_data['pos1'] = piece.piece.player.pos1
            piece_data['pos2'] = piece.piece.player.pos2

            result.append(piece_data)

        return {'data':result}

class UsingPieceApi(Resource):
    def get(self,user_id,piece_id):
        data = BagPiece.query.filter_by(user_id=user_id,piece_id=piece_id).all()
        result = []
        for piece in data:
            piece_data = {}
            piece_data['num'] = piece.num
            piece_data['total_num'] = piece.piece.total_num
            if piece_data['num'] < piece_data['total_num']:
                return "碎片不足"
            else:
                pass
                #if 没有，
                    # 合成一个球员，
                        #if ==
                            # 删除bag_piece
                #if 有， 返回提示


##
## Setup the Api resource routing here
##
bag_api.add_resource(BagPieceApi,'/pieces/<int:user_id>/')
bag_api.add_resource(UsingPieceApi,'/usingpiece/<int:user_id>/<int:piece_id>')