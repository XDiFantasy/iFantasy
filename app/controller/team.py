from flask import Blueprint
from flask_restful import Api, Resource
from app.model import BagPlayer, SeasonData, User,LineUp,TeamInfo
from app.controller import Message
from app import db

team_bp = Blueprint("team_bp", __name__)
team_api = Api(team_bp)


# 错误码 800-899
class TeamError:
    pass


# 返回给前端或安卓端的数据
class TeamMessage(Message):

    def __init__(self, result=None, error='', state=0):
        super(TeamMessage, self).__init__(result, error, state)


# 获取背包中所有球员信息,按照位置进行分类,默认是按照评分进行排序，也可以按照薪资排序
class AllPlayerAPi(Resource):

    def get(self, user_id, pos=None, order='score'):
        if order == 'score':
            data = BagPlayer.query.filter_by(user_id=user_id).order_by(BagPlayer.score.desc()).all()
        else:
            # assert order == 'salary'
            data = BagPlayer.query.filter_by(user_id=user_id).order_by(BagPlayer.salary.desc()).all()
        result = []
        if data is None or len(data) == 0:
            return TeamMessage(error="背包无球员", state=-801).response
        for player in data:
            if pos is not None:
                if player.player.pos1 != pos and player.player.pos2 != pos:
                    continue
                else:
                    tmp_pos = pos
            else:
                tmp_pos = player.player.pos1
            player_data = {}
            player_data['bag_player_id'] = player.id
            player_data['player_id'] = player.player.id
            player_data['name'] = player.player.name
            player_data['pos'] = tmp_pos
            player_data['score'] = player.score
            player_data['salary'] = player.salary

            result.append(player_data)

        return TeamMessage(result).response


# 获取单个球员的基本信息
class PlayerPersonApi(Resource):

    def get(self, bag_player_id):
        data = BagPlayer.query.filter_by(id=bag_player_id).first()
        if data is None:
            return TeamMessage(error="背包内无此球员信息", state=-802).response
        result = {}

        # TODO：臂展，站立身高的数据没有爬取到
        result['name'] = data.player.name
        result['team_name'] = data.player.team.name
        result['cloth_num'] = data.player.cloth_num
        result['pos'] = data.player.pos1  # 默认取球员第一个位置
        result['score'] = data.score
        result['salary'] = data.salary
        result['birthday'] = data.player.birthday
        result['country'] = data.player.country
        result['height'] = data.player.height
        result['weight'] = data.player.weight
        result['draft'] = data.player.draft  # 选秀
        result['contract'] = data.contract

        return TeamMessage(result).response


# TODO：投篮热图不知怎么做

# 获取单个球员赛季的数据,默认展示常规赛的数据，可以切换成季后赛的数据
class SeasonDataApi(Resource):
    # type为1表示常规赛数据，为0表示季后赛数据
    def get(self, player_id, type=1):
        if type == 1:
            data = SeasonData.query.filter_by(player_id=player_id).filter_by(is_regular=1).all()
        else:
            data = SeasonData.query.filter_by(player_id=player_id).filter_by(is_regular=0).all()

        if data is None or len(data) == 0:
            return TeamMessage(error="该球员无任何赛季数据", state=-803).response
        result = []

        for season in data:
            season_data = {}
            season_data['season'] = season.season
            season_data['team_name'] = season.team_name
            season_data['gp'] = season.gp  # 出场
            season_data['min'] = season.min  # 时间
            season_data['pts'] = season.pts  # 得分

            season_data['reb'] = season.reb  # 篮板
            season_data['ast'] = season.ast  # 助攻
            season_data['stl'] = season.stl  # 抢断
            season_data['blk'] = season.blk  # 盖帽
            season_data['tov'] = season.tov  # 失误
            season_data['fg_pct'] = season.fg_pct  # 投篮%
            season_data['fg3_pct'] = season.fg3_pct  # 三分%
            season_data['ft_pct'] = season.ft_pct  # 罚球%
            season_data['efg_pct'] = season.efg_pct
            season_data['ts_pct'] = season.ts_pct
            season_data['ortg'] = season.ortg
            season_data['drtg'] = season.drtg

            result.append(season_data)

        return TeamMessage(result).response

# 创建阵容
class AddLineupApi(Resource):

    def get(self,user_id):
        data = BagPlayer.query.filter_by(user_id=user_id).all()
        if data is None or len(data) == 0:
            return TeamMessage(error="您的背包无任何球员",state=-820).response
        res = []

        res_player = []
        for player in data:
            player_data = {}

            player_data['bag_player_id'] = player.id
            player_data['name'] = player.player.name
            player_data['pos'] = player.player.pos1
            player_data['score'] = player.score
            player_data['salary'] = player.salary

            res_player.append(player_data)

        team_datas = TeamInfo.query.all()
        if team_datas is None or len(team_datas) == 0:
            return TeamMessage(error="没有球队信息",state=-830).response
        res_team = []
        for team in team_datas:
            team_data = {}

            team_data['team_id'] = team.id
            team_data['name'] = team.name
            res_team.append(team_data)

        res.append(res_player)
        res.append(res_team)
        return TeamMessage(result=res).response

    def post(self):
        # TODO：创建阵容
        pass

# 获取用户阵容列表信息
class LineUpListApi(Resource):

    def get(self,user_id):
        data = LineUp.query.filter_by(user_id=user_id).all()
        if data is None or len(data) == 0:
            return TeamMessage(error="您还未创建阵容",state=-806).response
        res = []
        for lineup in data:
            lineup_data = {}
            lineup_data['lineup_id'] = lineup.id
            lineup_data['name'] = lineup.team_info.name

            res.append(lineup_data)

        return TeamMessage(result=res).response


# 替换球员
class ReplacePlayerApi(Resource):
    '''
    pos: C,PF,SF,SG,PG
    '''
    def get(self,lineup_id,bag_player_id,replace__player_id,pos):
        if bag_player_id == replace__player_id:
            return TeamMessage(error="不能替换自己",state=-840).response
        bag_player = BagPlayer.query.filter_by(id=bag_player_id).first()
        replace__player = BagPlayer.query.filter_by(id=replace__player_id).first()

        if bag_player is None:
            return TeamMessage(error="",state=-850).response

        if replace__player is None:
            return TeamMessage(error="",state=-850).response

        pos_bag = []
        pos_bag.append(bag_player.player.pos1)
        if bag_player.player.pos2 is not None:
            pos_bag.append(bag_player.player.pos2)

        db_pos = pos
        if len(db_pos) == 2:
            db_pos = pos[-1]
        if db_pos not in pos_bag:
            return TeamMessage(error="只能替换相同位置的球员",state=-860).response

        line_up = LineUp.query.filter_by(id=lineup_id).first()

        if line_up is None:
            return TeamMessage(error="你未创建该阵容",state=-861).response

        # 更换球员
        if pos == "C":
            line_up.c = bag_player_id
        elif pos == "PF":
            line_up.pf = bag_player_id
        elif pos == "SF":
            line_up.sf = bag_player_id
        elif pos == "SG":
            line_up.sg = bag_player_id
        elif pos == "PG":
            line_up.pg = bag_player_id

        db.session.commit()

        return TeamMessage(result="替换球员成功").response



# 解约球员，获得资金补贴
class DeletePlayerApi(Resource):

    def get(self, user_id, bag_player_id):
        bag_player = BagPlayer.query.filter_by(id=bag_player_id).first()
        if bag_player is None:
            return TeamMessage(error="不能删除背包不存在的球员", state=-804).response
        money = bag_player.salary
        db.session.delete(bag_player)
        user = User.query.filter_by(id=user_id).first()
        if user is None:
            return TeamMessage(error="该用户还未注册", state=-805).response
        user.money += money
        db.session.commit()

        return TeamMessage(result="删除成功").response


team_api.add_resource(AllPlayerAPi,
                      '/all/player/<int:user_id>',
                      '/all/player/<int:user_id>/ord/<string:order>',
                      '/all/player/<int:user_id>/pos/<string:pos>',
                      '/all/player/<int:user_id>/<string:pos>/<string:order>')

team_api.add_resource(PlayerPersonApi, '/per/player/<int:bag_player_id>')

team_api.add_resource(SeasonDataApi, '/season/<int:player_id>',
                      '/season/<int:player_id>/<int:type>')

team_api.add_resource(DeletePlayerApi, '/delete/<int:user_id>/<int:bag_player_id>')
