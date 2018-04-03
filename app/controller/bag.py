from flask import Blueprint
from flask_restful import Api, Resource,reqparse
from app import db
from app.model import BagPiece, BagEquip, BagProp, BagTrailCard
from app.model import BagPlayer,PropUsing
from app.controller import Message
from datetime import datetime

bag_bp = Blueprint('bag_bp', __name__)
bag_api = Api(bag_bp)

parser = reqparse.RequestParser()
query = db.session.query
add = db.session.add
commit = db.session.commit
rollback = db.session.rollback

class BagError:
    NO_PIECE = 'You have no pieces',  -301
    NO_TRAIL_CARD = 'You have no trail cards', -302
    NO_EQUIP = 'You have no equip', -303
    NO_PROP = 'You have no Prop', -304
    NOT_ENOUGH_PIECE = 'You have no enough piece', -305
    PLAYER_REPEAT = 'you already have this player', -306


class BagMessage(Message):
    PIECE_LIST = 'Piece list', 301
    USING_PIECE_ADD_PLAYER = 'Using piece add a player', 302

    TRAIL_CARD_LIST = 'Trail card list', 303
    USING_TRAIL_CARD_ADD_PLAYER = 'Using trail card add a player', 304
    USING_TRAIL_CARD_ADD_DUETIME = 'Using trail card add duetime', 305

    EQUIP_LIST = 'Bag equip list', 306
    USING_EQUIP = 'Using equip', 307

    PROP_LIST = 'Prop list', 308
    USING_PROP = 'Using prop', 309


    def __init__(self, result = None, error='', state=0):
        super(BagMessage, self).__init__(result, error, state)


#列出背包里的piece
class BagPieceApi(Resource):
    def get(self, user_id):
        data = BagPiece.query.filter_by(user_id=user_id).all()
        if data == None :
            return BagMessage(None, BagError.NO_PIECE).response

        result = []
        for each in data:
            each_data = {}
            each_data['name'] = each.piece.player.name
            each_data['num'] = each.num
            each_data['total'] = each.piece.total_num
            each_data['pos1'] = each.piece.player.pos1
            each_data['pos2'] = each.piece.player.pos2

            result.append(each_data)

        return BagMessage(result, BagMessage.PIECE_LIST).response


#使用piece合成player,
class UsingPieceApi(Resource):
    def post(self,user_id,player_id):
        # 判断该user是否已经有这个player
        if BagPlayer.query.filter_by(user_id=user_id,player_id=player_id).first() != None :
            return BagMessage(None, BagError.PLAYER_REPEAT).response

        data = BagPiece.query.filter_by(user_id=user_id, player_id=player_id).first()

        piece_data = {}
        piece_data['num'] = data.num
        piece_data['total_num'] = data.piece.total_num
        piece_data['name'] = data.piece.player.name

        #判断piece 是否足够合成
        if piece_data['num'] < piece_data['total_num']:
            return BagMessage(None,BagError.NOT_ENOUGH_PIECE).response

        # 消耗使用的piece
        if piece_data['num'] == piece_data['total_num']:
            delete(data)
            commit()
        else:
            new_num = piece_data['num'] - piece_data['total_num']
            data.update({'num': new_num})
            commit()
        # 合成player
        today = datetime.now()
        due = today.replace(year = today.year + 1)
        player = db.session.query(PlayerBase).get(player_id = player_id)
        contract = '一年%d万，%d年%d月%d日签约，%d年%d月%d日到期' % (player.price, today.year,
                   today.month, today.day, due.year, due.month, due.day)
        add(BagPlayer(user_id,player_id,player.score,player.price,None,due,contract))
        return BagMessage(player.name,BagMessage.USING_PIECE_ADD_PLAYER).response

#列出bag里的trail_card
class BagTrailCardApi(Resource):
    def get(self, user_id):
        data = BagTrailCard.query.filter_by(user_id=user_id).all()
        if data == None:
            return BagMessage(None, BagError.NO_TRAIL_CARD).response

        result = []
        for each in data:
            each_data = {}
            each_data['name'] = each.player.name
            each_data['num'] = each.num
            each_data['time'] = each.time
            each_data['pos1'] = each.player.pos1
            each_data['pos2'] = each.player.pos2

            result.append(each_data)
        return BagMessage(result, BagMessage.TRAIL_CARD_LIST).response

#使用trail card 增加player/duetime
class UsingTrailCardApi(Resource):
    def post(self,user_id,player_id,time):
        playerdata = BagPlayer.query.filter_by(user_id=user_id,player_id=player_id).first()

        #若已有player,续duetime
        if playerdata != None:
            timedata = playerdata.duetime
            timedata += timedelta(day = time)
            commit()
            return BagMessage(playerdata.name, BagMessage.USING_TRAIL_CARD_ADD_DUETIME).response
        #若没有player,add a player
        else:
            today = datetime.today()
            due = today.replace(day = today.day + time)
            player = query(PlayerBase).get(player_id)
            contract = '%d年%d月%d日，%d年%d月%d日到期' % (today.year, today.month, today.day, due.year, due.month, due.day)
            add(BagPlayer(user_id, player_id, player.score, player.price, None, due, contract))
            commit
            return BagMessage(player.name, BagMessage.USING_TRAIL_CARD_ADD_PLAYER).response


#列出背包里的装备
#目前还没有设计具体装备，预留接口
class BagEquipApi(Resource):
    def get(self, user_id):
        data = BagEquip.query.filter_by(user_id).all()
        if data == None:
            return BagMessage(None,BagError.NO_EQUIP).response

        result = []
        for each in data:
            each_data = {}
            each_data['name'] = each.equip.name
            each_data['num'] = each.num
            each_data['attr_ch_id'] = each.equip.attr_ch_id

            result.append(each_data)
        return BagMessage(result, BagMessage.EQUIP_LIST).response

#使用bag里的equip
#目前没有equip,这里先预留接口
#好像只能留空接口
class UsingEquipApi(Resource):
    def post(self, user_id, equip_id):
        pass


class BagPropApi(Resource):
    def get(self, user_id):
        data = query(BagProp).get(user_id).first()
        #若没有，则记为各拥有０个fund_card,exp_card
        if data == None or len(data) == 0:
            add(BagProp(user_id= user_id,fund_card_num= 0,exp_card_num= 0))
            commit
        result = {}
        result['fund_card_num'] = data.fund_card_num
        result['exp_card_num'] = data.exp_card_num
        return BagMessage(result, BagMessage.PROP_LIST).response

class UsingPropApi(Resource):
    def post(self, user_id, prop_type):
        data = query(BagProp).get(user_id = user_id)
        if data == None or len(data) == 0:
            return BagMessage(None, BagError.NO_PROP)
        #0为fund_card,1为exp_card
        usingdata = query(PropUsing).get(user_id= user_id,prop_type= prop_id)
        if usingdata == None or len(usingdata) == 0:
            now = datetime.now()
            due = now.replace(day= now.day + 3)
            add(usingdata= PropUsing(user_id= user_id, prop_type= prop_type, duetime= due))
            commit
        else:
            due = usingdata.duetime.replace(day= usingdata.duetime + 3)
            commit

            return BagMessage(usingdata,BagMessage.USING_PROP).response




##
## Setup the Api resource routing here
##
bag_api.add_resource(BagPieceApi,'/piecelist/<int:user_id>')
bag_api.add_resource(UsingPieceApi,'/usingpiece/<int:user_id>/<int:player_id>')
bag_api.add_resource(BagTrailCardApi,'/trailcardlist/<int:user_id>')
bag_api.add_resource(UsingTrailCardApi,'/usingtrailcard/<int:user_id>/<int:player_id>')
bag_api.add_resource(BagEquipApi,'/equiplist/<int:user_id>')
bag_api.add_resource(UsingEquipApi,'/usingequip/<int:user_id>/<int:equip_id>')
bag_api.add_resource(BagPropApi,'/proplist/<int:user_id>')
bag_api.add_resource(UsingPropApi,'/usingprop/<int:user_id>/<int:prop_type>')
