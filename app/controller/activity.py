from flask import Blueprint, jsonify, request, abort
from flask_restful import Api, Resource
from app.model import Theme, VipCard, User, Vip, Fund, FundType
from app.controller.message import Message
from app import db
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError

activity_bp = Blueprint('activity_bp', __name__)
activity_api = Api(activity_bp)

query = db.session.query

# your code
class apiForTheme(Resource):
	def get(self):
		rows = list()
		try:
			rows = query(Theme).all()
		except:
			mes = Message(error='Database Query Error', state=-1)
			return mes.response
		data = list()
		for row in rows:
			data.append({'id':row.id,'title':row.title, 'detail':row.detail, 'price':row.price})
		return Message(data).response

class apiForVip(Resource):
	card_type = ['week','month','year','permanent']
	duration = [7,30,365,9999]

	def get(self):
		# get prices of all four types of vip
		res = dict()
		for card in self.card_type:
			index = self.card_type.index(card)
			try:		
				res[card] = query(VipCard).filter_by(time = self.duration[index]).first().price
			except:
				return Message(error='Database Query Error', state=-1).response
		return Message(res).response
		
	def post(self):
		# playerId buys vipType

		if 'playerId' not in  request.args or 'vipType' not in request.args:
			return Message(error='Args Type Error',state=-1).response

		playerId = request.args['playerId'].lower()
		vipType = request.args['vipType'].lower()

		# check if vipType is valid
		if_vipType_exists = False
		for card in self.card_type:
			if vipType == card:
				if_vipType_exists = True
		if not if_vipType_exists:
			return Message(error='Arg Error: typeId does not exist in Database', state=-1).response

		# check if playerId exists in table User
		if_playerId_exists_in_user = False if len(query(User).filter_by(id = playerId).all()) == 0 else True
		if not if_playerId_exists_in_user:
			return Message(error='Arg Error: playerId does not exist in Database', state=-1).response

		# check if playerId has enough money
		try:
			index = self.card_type.index(vipType)
			money_left = query(User).filter_by(id = playerId).first().money
			money_needed = query(VipCard).filter_by(time = self.duration[index]).first().price
		except:
			return Message(error='Database Query Error', state=-1).response
		if money_left <= money_needed:
			return Message(error='Not enough money in account', state=-1).response
		
		# update playerId's money in account
		try:
			this_user = query(User).filter_by(id = playerId).first()
			this_user.money -= money_needed
			db.session.commit()
		except:
			return Message(error='Database Update Error', state=-1).response

		# check if playerId exists in table Vip, compute the next duedate
		time_delta = timedelta(days = self.duration[self.card_type.index(vipType)])
		if_playerId_exists_in_vip = False if len(query(Vip).filter_by(user_id = playerId).all()) == 0 else True
		duedate_before = query(Vip).filter_by(user_id = playerId).first().duedate if if_playerId_exists_in_vip else datetime.now()
		duedate_after = duedate_before + time_delta
		if if_playerId_exists_in_vip:
			try:
				row = query(Vip).filter_by(user_id = playerId).first()
				row.duedate = duedate_after
				db.session.commit()
			except:
				return Message(error='Database Update Error', state=-1).response
		else:
			row = Vip(user_id = playerId, level = 1, active = True, duedate = duedate_after)
			try:
				db.session.add(row)
				db.session.commit()
			except:
				return Message(error='Database Insert Error', state=-1).response
		return Message().response
			

class apiForFinance(Resource):
	def get(self):
		# get all finance products
		try:
			rows = query(FundType).all()
		except:
			return Message(error='Database Query Error', state=-1).response
		data = list()
		for row in rows:
			data.append({'price':row.price, 'rate': row.rate})
		return Message(data).response
	
	# def post(self):
	# 	# playerId buys a financeType

activity_api.add_resource(apiForTheme, '/theme/')
activity_api.add_resource(apiForVip, '/vip/')
activity_api.add_resource(apiForFinance, '/finance/')