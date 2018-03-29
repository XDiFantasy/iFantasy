from flask import Blueprint
from flask_restful import Api, Resource
from app.model.team import PlayerBase,BagPlayer

team_bp = Blueprint("team_bp", __name__)
team_api = Api(team_bp)


# 获取背包中所有球员信息,按照位置进行分类,默认是按照评分进行排序
class AllPlayerAPi(Resource):

    def get(self, user_id, pos=None, order='score'):
        if order == 'score':
            data = BagPlayer.query.filter_by(user_id=user_id).order_by(BagPlayer.score.desc()).all()
        else:
            assert order == 'salary'
            data = BagPlayer.query.filter_by(user_id=user_id).order_by(BagPlayer.salary.desc()).all()
        result = []
        if data is None or len(data) == 0:
            return {'data': '你的背包无任何球员', 'message': 'ok'}
        for player in data:
            if pos is not None:
                if player.player.pos1 != pos and player.player.pos2 != pos:
                    continue
            player_data = {}
            player_data['player_id'] = player.player.id
            player_data['name'] = player.player.name
            player_data['pos1'] = player.player.pos1
            player_data['pos2'] = player.player.pos2
            player_data['score'] = player.score
            player_data['salary'] = player.salary

            result.append(player_data)

        return {'data': result, 'message': 'ok'}

# 获取单个球员信息
class PlayerPersonApi(Resource):

    def get(self, player_id):
        data = PlayerBase.query.filter_by(id=player_id).first()
        if data is None:
            return {'message': '数据库无此球员信息'}
        result = {}
        result['name'] = data.name
        result['pos1'] = data.pos1
        result['price'] = data.price
        result['score'] = data.score

        return {'data': result, 'message': 'ok'}


team_api.add_resource(AllPlayerAPi,
                      '/all/player/<int:user_id>/',
                      '/all/player/<int:user_id>/ord/<string:order>/',
                      '/all/player/<int:user_id>/pos/<string:pos>/',
                      '/all/player/<int:user_id>/<string:pos>/<string:order>/')

team_api.add_resource(PlayerPersonApi,'/per/player/<int:player_id>/')
