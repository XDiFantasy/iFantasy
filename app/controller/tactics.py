from flask import Blueprint

from flask_restful import Api, Resource, reqparse
from app import db
from app.controller import Message
from app.model.tactics import OStrategy, AttrCh, DStrategy
from app.model.team import BagPlayer, LineUp, SeasonData, PlayerBase

tactics_bp = Blueprint("tactics_bp", __name__)
tactics_api = Api(tactics_bp)

query = db.session.query

OFFENSE_STRATEGY = {
    'strategy_1': {'strategy': '外线投射：通过无球掩护为PG、SG、SF提供外线投篮机会，较为克制内线包夹，' \
                               '内线联防的防守战术。适合拥有强力外线得分能力的PG、SG、SF的队伍。'},
    'strategy_2': {'strategy': '挡拆外切：挡拆人提到上线为持球人做墙，做墙后持球人持球冲击内线带走两个防守人，' \
                               '并随时准备将球进行传导刚才挡拆者；做墙者来到甜点区准备出手中距离或三分球。此战术适用于有中远距离能力的内线球员。'},
    'strategy_3': {'strategy': '突破分球：本方队员篮下得分困难，中远距离投篮又没有机会时，' \
                               '进攻队员可以选择突破分球，有目的地将对手挤向篮下，迫使对手缩小防守区域，' \
                               '并及时将球传给跟进或绕到无人防守处的接应队员。这种突破分球的战术不是为了篮下得分，' \
                               '而是为了给同伴中远距离投篮和空切上篮创造机会。'},
    'strategy_4': {'strategy': '内线强攻：清空强侧，给PF，C单打的机会。适合内线能力较强的球队。'},
    'strategy_5': {'strategy': '双塔战术：适用于同时拥有能力较强的PF、和C的球队，双塔战术利用两个球员强大的内线牵制力，' \
                               '对对手内线造成更大的破坏。'},
    'strategy_6': {'strategy': '掩护内切：挡拆人提到上线为持球人做墙，做墙后持球人持球冲击内线一侧带走两个防守人，' \
                               '并随时准备将球进行传导刚才挡拆者；做墙者来到另一侧准备接球上篮。此战术适用于内线终结能力较强的球员。'},
    'strategy_7': {'strategy': '普林斯顿体系：普林斯顿强调中锋调度和人人为我，我为人人的概念，坚持团队篮球和团队精神' \
                               '在全队能力值偏低的情况下，提升球队战力。'},
}

DEFENSE_STRATEGY = {
    'strategy_8': {'strategy': '外线紧逼：PG、SG、SF提升外防守效率，降低对方外线投射效率，增加对方失误数量。'},
    'strategy_9': {'strategy': '外线联防：对方PG、SG、SF有一个或两个为精英外线时，可采用联防，增加被包夹人失误率，' \
                               '但同时提高空位球员命中率。'},
    'strategy_10': {'strategy': '内线包夹：对方C、PF能力值较高时，可采用包夹，增加失误率，增加未被包夹球员命中率。'},
    'strategy_11': {'strategy': '二三联防：五个球员位置基本固定，每个球员防守覆盖一定区域，二三联防强调团队整体的防守存在感，压迫对手持球，' \
                                '增加对手失误。适用于每个人防守能力或几个球员防守一般的球员。'},
}


# 策略类状态码
class TacError:
    No_Arg = 'Request denied', -111
    No_LineUp = 'You have no such lineup.', -101
    No_Player = 'You have no such player.', -102
    No_Data = 'You have no data.', -103
    No_OIndex = 'You have no such offensive index.', -104
    No_DIndex = 'You have no such defensive index.', -105
    No_Recommend = 'Your lineup suits no tactics.', -106


# 策略类信息传递
class TacMessage(Message):
    def __init__(self, result=None, error='', state=0):
        super(TacMessage, self).__init__(result, error, state)


# 进攻战术介绍
class Offense_strategy_IndexAPi(Resource):
    def get(self, key):
        if key is None:
            return TacMessage(None, *TacError.No_OIndex).response
        return TacMessage(result=OFFENSE_STRATEGY[key], state=0).response


# 防守战术介绍
class Defense_Strategy_IndexAPi(Resource):
    def get(self, key):
        if key is None:
            return TacMessage(None, *TacError.No_DIndex).response
        return TacMessage(result=DEFENSE_STRATEGY[key], state=0).response


class Score_APi(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("user_id", type=int)

    def get(self):
        args = self.parser.parse_args()
        user_id = args['user_id']
        if user_id is None:
            return TacMessage(None, *TacError.No_Arg).response
        data = query(LineUp).filter_by(user_id=user_id).first()
        if data is None:
            return TacMessage(None, *TacError.No_Player).response
        pg = data.pg
        sg = data.sg
        sf = data.sf
        pf = data.pf
        c = data.c
        pg_data = query(BagPlayer).filter_by(id=data.pg).first()
        sg_data = query(BagPlayer).filter_by(id=data.sg).first()
        sf_data = query(BagPlayer).filter_by(id=data.sf).first()
        pf_data = query(BagPlayer).filter_by(id=data.pf).first()
        c_data = query(BagPlayer).filter_by(id=data.c).first()
        score = pg_data.score + sg_data.score + sf_data.score + pf_data.score + c_data.score
        return TacMessage(result=score,state=0).response
    


# 请一个用户ID下来，通过用户ID访问阵容，利用阵容中的球员ID访问球员的SeasonData
class OStrategy_RecommendAPi(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("user_id", type=int)

    def get(self):
        args = self.parser.parse_args()
        user_id = args['user_id']
        if user_id is None:
            return TacMessage(None, *TacError.No_Arg).response
        data = query(LineUp).filter_by(user_id=user_id).first()
        if data is None:
            return TacMessage(None, *TacError.No_Data).response
        pg = query(BagPlayer).filter_by(id=data.pg).first()
        sg = query(BagPlayer).filter_by(id=data.sg).first()
        sf = query(BagPlayer).filter_by(id=data.sf).first()
        pf = query(BagPlayer).filter_by(id=data.pf).first()
        c = query(BagPlayer).filter_by(id=data.c).first()
        pg_id = pg.player_id
        sg_id = sg.player_id
        sf_id = sf.player_id
        pf_id = pf.player_id
        c_id = c.player_id
        recommend = {}
        random1 = query(SeasonData).filter_by(player_id=pg_id).first()
        random2 = query(SeasonData).filter_by(player_id=sg_id).first()
        random3 = query(SeasonData).filter_by(player_id=sf_id).first()
        random4 = query(SeasonData).filter_by(player_id=pf_id).first()
        random5 = query(SeasonData).filter_by(player_id=c_id).first()
        if random1 is None or random2 is None or random3 is None or random4 is None or random5 is None:
                return TacMessage(None, *TacError.No_Data).response

        

        # 挡拆外切
        if random1.fg3_pct > 0.33 or random2.fg3_pct > 0.33:
            recommend['1st ostrategy'] = 1

        # 外线投射
        if random1.fg3_pct > 0.33 or random2.fg3_pct > 0.33 or random2.fg3_pct > 0.33:
            recommend['2nd ostrategy'] = 2

        # 突破分球
        if (random1.fg3_pct < 0.27 or random2.fg3_pct < 0.27) and (
                random3.fg_pct < 0.45 or random4.fg_pct < 0.45):
            recommend['3rd ostrategy'] = 3

        # 内线强攻
        if random1.fg_pct > 0.5 or random2.fg_pct > 0.52:
            recommend['4th ostrategy'] = 4

        # 双塔战术
        if random1.ast > 2 and random2.ast > 2:
            recommend['5th ostrategy'] = 5

        # 掩护内切
        if random1.fg_pct > 0.53 or random2.fg_pct > 0.55:
            recommend['6th ostrategy'] = 6

        # 普林斯顿体系
        random1 = query(PlayerBase).filter_by(id=pg_id).first()
        random2 = query(PlayerBase).filter_by(id=sg_id).first()
        random3 = query(PlayerBase).filter_by(id=sf_id).first()
        random4 = query(PlayerBase).filter_by(id=pf_id).first()
        random5 = query(PlayerBase).filter_by(id=c_id).first()
        if random1 is None or random2 is None or random3 is None or random4 is None or random5 is None:
            return TacMessage(None, *TacError.No_Data).response
        
        if random1.score < 15 and random2.score < 15 and random3.score < 15 and random4.score < 15 and \
                random5.score > 25:
            recommend['7th ostrategy'] = 7

        # 没有推荐战术
        if recommend is None:
            return TacMessage(None, *TacError.No_Recommend).response

        return TacMessage(result=recommend,state=0).response


# 防守战术推荐
class DStrategy_RecommendAPi(Resource):
    parser = reqparse.RequestParser()
    # 请求下来对方user_id
    parser.add_argument("user_id", type=int)

    def get(self):
        args = self.parser.parse_args()
        user_id = args['user_id']

        if user_id is None:
            return TacMessage(None, *TacError.No_Arg).response
        data = query(LineUp).filter_by(user_id=user_id).first()
        if data is None:
            return TacMessage(None, *TacError.No_Data).response
        pg = query(BagPlayer).filter_by(id=data.pg).first()
        sg = query(BagPlayer).filter_by(id=data.sg).first()
        sf = query(BagPlayer).filter_by(id=data.sf).first()
        pf = query(BagPlayer).filter_by(id=data.pf).first()
        c = query(BagPlayer).filter_by(id=data.c).first()
        pg_id = pg.player_id
        sg_id = sg.player_id
        sf_id = sf.player_id
        pf_id = pf.player_id
        c_id = c.player_id
        random1 = query(SeasonData).filter_by(player_id=pg_id).first()
        random2 = query(SeasonData).filter_by(player_id=sg_id).first()
        random3 = query(SeasonData).filter_by(player_id=sf_id).first()
        random4 = query(SeasonData).filter_by(player_id=pf_id).first()
        random5 = query(SeasonData).filter_by(player_id=c_id).first()
        if random1 is None or random2 is None or random3 is None or random4 is None or random5 is None:
            return TacMessage(None, *TacError.No_Data).response

        recommend = {}

        # 外线紧逼
          if random1.fg3_pct > 0.33 or random2.fg3_pct > 0.33 or random3.fg3_pct > 0.33:
              recommend['1st dstrategy'] = 1

        # 二三联防
          if random1.ortg > 103.7696 and random2.ortg > 103.7696 and random3.ortg > 103.5955 and random4.ortg > 103.5955 \
                    and random5.ortg > 103.4155:
             recommend['2nd dstrategy'] = 2
        random1 = query(PlayerBase).filter_by(player_id=pg_id).first()
        random2 = query(PlayerBase).filter_by(player_id=sg_id).first()
        random3 = query(PlayerBase).filter_by(player_id=sf_id).first()
        random4 = query(PlayerBase).filter_by(player_id=pf_id).first()
        random5 = query(PlayerBase).filter_by(player_id=c_id).first()
            if random1 is None or random2 is None or random3 is None or random4 is None or random5 is None:
                return TacMessage(None, *TacError.No_Data).response

        # 外线包夹
          if random1.score > 10 or random2.score > 10 or random3.score > 10:
              recommend['3rd dstrategy'] = 3

        # 内线包夹
          if random1.score > 30 or random2.score > 30:
              recommend['4th dstrategy'] = 4

          if recommend is None:
              return TacMessage(None, *TacError.No_Recommend).response

          return TacMessage(result=recommend,state=0).response


class OffStrategy_InstallAPi(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("offstrategy_id", type=int)

    def get(self):
        args = self.parser.parse_args()
        if args is None:
            return TacMessage(None, *TacError.No_Arg).response
        off_id = args['offstrategy_id']
        data = query(OStrategy).filter_by(id=off_id).first()
        if data is None:
            return TacMessage(None, *TacError.No_Data).response
        result = dict()
        result['id'] = data.id
        result['intro'] = data.intro
        result['pg'] = data.pg
        result['sg'] = data.sg
        result['sf'] = data.sf
        result['pf'] = data.pf
        result['c'] = data.c
        return TacMessage(result=result,state=0).response


class DefStrategy_InstallAPi(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("defstrategy_id", type=int)

    def get(self):
        args = self.parser.parse_args()
        if args is None:
            return TacMessage(None,*TacError.No_Arg).response
        defstrategy_id = args['defstrategy_id']
        data = query(DStrategy).filter_by(id=defstrategy_id).first()
        if data is None:
            return TacMessage(None, *TacError.No_Data).response
        result = dict()
        result['id'] = data.id
        result['intro'] = data.intro
        result['pg'] = data.pg
        result['sg'] = data.sg
        result['sf'] = data.sf
        result['pf'] = data.pf
        result['c'] = data.c
        return TacMessage(result=result,state=0).response


tactics_api.add_resource(Offense_strategy_IndexAPi, '/off_strategy/<key>')

tactics_api.add_resource(Defense_Strategy_IndexAPi, '/def_strategy/<key>')

tactics_api.add_resource(OStrategy_RecommendAPi, '/ostrategy_recommend')

tactics_api.add_resource(DStrategy_RecommendAPi, '/dstrategy_recommend')

tactics_api.add_resource(Score_APi, '/score')

tactics_api.add_resource(OffStrategy_InstallAPi, '/offstrategy_install')

tactics_api.add_resource(DefStrategy_InstallAPi, '/defstrategy_install')
