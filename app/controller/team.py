from flask import Blueprint
from flask_restful import Api, Resource, reqparse
from app.model import BagPlayer, SeasonData, User, LineUp, TeamInfo
from app.controller import Message
from app import db
from sqlalchemy import or_

team_bp = Blueprint("team_bp", __name__)
team_api = Api(team_bp)

'''
 返回球员的位置
'''
def get_pos(bag_player):
    pos = []
    pos.append(bag_player.player.pos1)
    if bag_player.player.pos2:
        pos.append(bag_player.player.pos2)
    return pos


'''
返回球员的信息:名字 位置 背包ID
'''
def get_player_info(bag_player_id, pos):
    bag_player = BagPlayer.query.filter_by(id=bag_player_id).first()
    if bag_player is None:
        return False, "背包无此球员"
    res = {}
    res['bag_player_id'] = bag_player_id
    res['pos'] = pos
    res['name'] = bag_player.player.name

    return True, res


# 错误码 800-899
class TeamError:
    pass


# 返回给前端或安卓端的数据
class TeamMessage(Message):

    def __init__(self, result=None, error='', state=0):
        super(TeamMessage, self).__init__(result, error, state)


# 获取背包中所有球员信息,按照位置进行分类,默认是按照评分进行排序，也可以按照薪资排序
class AllPlayerAPi(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument("user_id", type=int)
    parser.add_argument("pos", type=str)
    parser.add_argument("order", type=str)

    def get(self):
        args = self.parser.parse_args()
        user_id = args['user_id']
        # print(user_id)
        if args['order'] is None or args['order'] == '' or args['order'] == 'score':
            order = 'score'
        else:
            order = 'salary'

        pos = args['pos']
        # print(type(pos))
        # print(pos)
        # print(order)
        if order == 'score':
            data = BagPlayer.query.filter_by(user_id=user_id).order_by(BagPlayer.score.desc()).all()
        else:
            # assert order == 'salary'
            data = BagPlayer.query.filter_by(user_id=user_id).order_by(BagPlayer.salary.desc()).all()
        result = []
        if data is None or len(data) == 0:
            return TeamMessage(error="背包无球员", state=-801).response
        for player in data:
            if pos is not None and pos != '':
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

    parser = reqparse.RequestParser()
    parser.add_argument("bag_player_id", type=int)

    def get(self):
        args = self.parser.parse_args()
        bag_player_id = args['bag_player_id']

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
    parser = reqparse.RequestParser()
    parser.add_argument("bag_player_id", type=int)
    parser.add_argument("type",type=int)

    def get(self):
        args = self.parser.parse_args()
        bag_player_id = args['bag_player_id']

        bag_player = BagPlayer.query.filter_by(id=bag_player_id).first()
        if bag_player is None:
            return TeamMessage(error="背包无此球员",state=-832).response
        player_id = bag_player.player.id

        type = args['type']

        if type is None or type == '':
            type = 1

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
    '''
     pos: c,pf,sf,pg,sg 的顺序
    '''

    parser = reqparse.RequestParser()
    parser.add_argument("user_id", type=int)
    parser.add_argument("team_id", type=int)
    parser.add_argument("c", type=int)
    parser.add_argument("pf", type=int)
    parser.add_argument("sf", type=int)
    parser.add_argument("pg", type=int)
    parser.add_argument("sg", type=int)
    parser.add_argument('strategy_id',type=int)

    '''
    返回背包拥有的球员信息 所有队伍的信息
    '''
    def get(self):
        args = self.parser.parse_args()
        user_id = args['user_id']
        data = BagPlayer.query.filter_by(user_id=user_id).all()
        if data is None or len(data) == 0:
            return TeamMessage(error="您的背包无任何球员", state=-820).response
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
            return TeamMessage(error="没有球队信息", state=-830).response
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
        args = self.parser.parse_args(strict=True)

        user_id = args['user_id']
        team_id = args['team_id']
        player_id_c = args['c']
        player_id_pf = args['pf']
        player_id_sf = args['sf']
        player_id_pg = args['pg']
        player_id_sg = args['sg']
        strategy_id = args['strategy_id']

        print(user_id)
        print(team_id)
        players = [player_id_c,player_id_pf,player_id_sf,player_id_pg,player_id_sg]
        player_len = 0
        for player in players:
            if player is not None:
                player_len += 1

        if player_len == 0:
            return TeamMessage(error="未选中任何球员", state=-880).response
        if player_len < 5:
            return TeamMessage(error="球员未满5人,无法组建球队", state=-845).response


        player_c = BagPlayer.query.filter_by(id=player_id_c).first()
        player_pf = BagPlayer.query.filter_by(id=player_id_pf).first()
        player_sf = BagPlayer.query.filter_by(id=player_id_sf).first()
        player_pg = BagPlayer.query.filter_by(id=player_id_pg).first()
        player_sg = BagPlayer.query.filter_by(id=player_id_sg).first()

        if player_c is None or player_pf is None or player_sf is None or player_pg is None or player_sg is None:
            return TeamMessage(error="无此球员信息", state=-851).response

        if 'C' not in get_pos(player_c):
            return TeamMessage(error="球员无法打C位置", state=-855).response
        if 'F' not in get_pos(player_pf):
            return TeamMessage(error="球员无法打PF位置", state=-856).response
        if 'F' not in get_pos(player_sf):
            return TeamMessage(error="球员无法打SF位置", state=-857).response
        if 'G' not in get_pos(player_pg):
            return TeamMessage(error="球员无法打PG位置", state=-858).response
        if 'G' not in get_pos(player_sg):
            return TeamMessage(error="球员无法打SG位置", state=-859).response

        lineup = LineUp(user_id=user_id, team_id=team_id, pf=player_id_pf, c=player_id_c, sf=player_id_sf,
                        sg=player_id_sg, pg=player_id_pg,strategy_id=strategy_id)
        db.session.add(lineup)

        db.session.commit()

        return TeamMessage(result="创建阵容成功").response


# 获取用户阵容列表信息
class LineUpListApi(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument("user_id", type=int)

    def get(self):
        args = self.parser.parse_args()
        user_id = args['user_id']
        data = LineUp.query.filter_by(user_id=user_id).all()
        if data is None or len(data) == 0:
            return TeamMessage(error="您还未创建阵容", state=-806).response
        res = []
        for lineup in data:
            lineup_data = {}
            lineup_data['lineup_id'] = lineup.id
            lineup_data['name'] = lineup.team_info.name

            res.append(lineup_data)

        return TeamMessage(result=res).response


# 获取阵容球员信息
class LineupPlayerApi(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("lineup_id", type=int)

    def get(self):
        args = self.parser.parse_args()
        if 'lineup_id' not in args:
            return TeamMessage(error="不能没有阵容", state=-840).response
        lineup_id = args['lineup_id']

        lineup = LineUp.query.filter_by(id=lineup_id).first()
        if lineup is None:
            return TeamMessage(error="无此阵容信息", state=-841).response

        flag, res_c = get_player_info(lineup.c, 'C')
        if not flag:
            return TeamMessage(error=res_c, state=-842).response
        flag, res_pf = get_player_info(lineup.pf, 'PF')
        if not flag:
            return TeamMessage(error=res_pf, state=-842).response
        flag, res_sf = get_player_info(lineup.sf, 'SF')
        if not flag:
            return TeamMessage(error=res_sf, state=-842).response
        flag, res_pg = get_player_info(lineup.pg, 'PG')
        if not flag:
            return TeamMessage(error=res_pg, state=-842).response
        flag, res_sg = get_player_info(lineup.sg, 'SG')
        if not flag:
            return TeamMessage(error=res_sg, state=-842).response

        res = [res_c, res_pf, res_sf, res_pg, res_sg]

        return TeamMessage(result=res).response


# 替换球员
class ReplacePlayerApi(Resource):
    '''
    pos: C,PF,SF,SG,PG
    '''
    parser = reqparse.RequestParser()
    parser.add_argument("lineup_id", type=int)
    parser.add_argument("bag_player_id", type=int)
    parser.add_argument("replace_player_id", type=int)
    parser.add_argument("pos", type=str)


    def put(self):
        args = self.parser.parse_args()
        lineup_id = args['lineup_id']
        bag_player_id = args['bag_player_id']
        replace_player_id = args['replace_player_id']
        pos = args['pos']
        if bag_player_id == replace_player_id:
            return TeamMessage(error="不能替换自己", state=-840).response

        line_up = LineUp.query.filter_by(id=lineup_id).first()
        if line_up is None:
            return TeamMessage(error="你未创建该阵容", state=-861).response

        lineup_player_ids = [line_up.c,line_up.pf,line_up.sf,line_up.pg,line_up.sg]
        if bag_player_id in lineup_player_ids:
            return TeamMessage(error="阵容已有该球员",state=-862).response

        bag_player = BagPlayer.query.filter_by(id=bag_player_id).first()
        replace_player = BagPlayer.query.filter_by(id=replace_player_id).first()

        if bag_player is None:
            return TeamMessage(error="无此球员信息", state=-850).response

        if replace_player is None:
            return TeamMessage(error="无此球员信息", state=-850).response

        db_pos = pos
        if len(db_pos) == 2:
            db_pos = pos[-1]
        if db_pos not in get_pos(bag_player):
            return TeamMessage(error="只能替换相同位置的球员", state=-860).response

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

    parser = reqparse.RequestParser()
    parser.add_argument("user_id", type=int)
    parser.add_argument("bag_player_id", type=int)

    def delete(self):
        args = self.parser.parse_args()
        user_id = args['user_id']
        bag_player_id = args['bag_player_id']
        print(user_id)
        print(bag_player_id)

        user = User.query.filter_by(id=user_id).first()
        if user is None:
            return TeamMessage(error="该用户还未注册", state=-805).response

        bag_player = BagPlayer.query.filter_by(id=bag_player_id).first()
        if bag_player is None:
            return TeamMessage(error="不能删除背包不存在的球员", state=-804).response
        lineups = LineUp.query.filter(
            or_(LineUp.c == bag_player_id, LineUp.pf == bag_player_id, LineUp.sf == bag_player_id,
                LineUp.pg == bag_player_id, LineUp.sg == bag_player_id)).all()
        if lineups is not None:
            for lineup in lineups:
                db.session.delete(lineup)
        money = bag_player.salary
        db.session.delete(bag_player)

        user.money += money
        db.session.commit()

        return TeamMessage(result="删除成功,获取补贴{} 万元".format(money)).response


team_api.add_resource(AllPlayerAPi,'/all/player')

team_api.add_resource(PlayerPersonApi, '/per/player')

team_api.add_resource(SeasonDataApi, '/season')

team_api.add_resource(AddLineupApi,'/add/lineup')

team_api.add_resource(LineUpListApi,'/lineup/list')

team_api.add_resource(LineupPlayerApi,'/lineup/player')

team_api.add_resource(ReplacePlayerApi,'/replace/player')

team_api.add_resource(DeletePlayerApi, '/delete/player')
