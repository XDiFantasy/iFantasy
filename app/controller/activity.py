from flask import Blueprint, jsonify, request, abort
from flask_restful import Api, Resource
from app.model import Theme, VipCard, User, Vip
from app import db
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError

activity_bp = Blueprint('activity_bp', __name__)
activity_api = Api(activity_bp)


# your code
class apiForTheme(Resource):
	def get(self):
		try:
			rows = db.session.query(Theme).all()
		except IntegrityError as error:
			#  TODO: error handling	
		data = list()
		for row in rows:
			data.append({'id':row.id,'title':row.title, 'detial':row.detail, 'price':row.price})
		res = {'length':len(rows),'items':data}
		return jsonify(res)

class apiForVip(Resource):
	card_type = ['week','month','year','permanent']
	duration = [7,30,365,9999]

	def get(self):
		# get prices of all four types of vip
		res = dict()
		for card in self.card_type:
			index = self.card_type.index(card)
			try:		
				res[card] = db.session.query(VipCard).filter_by(time = self.duration[index]).first().price
			except IntegrityError as error:
				#  TODO: error handling
		return jsonify(res)
		
	def post(self):
		# playerId buys vipType
		if 'playerId' in  request.args and 'vipType' in request.args:
			playerId = request.args['playerId']
			vipType = request.args['vipType']

			# check if vipType is valid
			if_vipType_exists = False
			for card in self.card_type:
				if vipType == card:
					if_vipType_exists = True
			if not if_vipType_exists:
				#  TODO: error handling

			# check if playerId exists in table User
			if_playerId_exists_in_user = False if len(db.session.query(User).filter_by(id = playerId).all()) == 0 else True
			if not if_playerId_exists_in_user:
				#  TODO: error handling

			# check if playerId exists in table Vip, compute the next duedate
			time_delta = timedelta(days = self.duration[self.card_type.index(vipType)])
			if_playerId_exists_in_vip = False if len(db.session.query(Vip).filter_by(user_id = playerId).all()) == 0 else True
			duedate_before = db.session.query(Vip).filter_by(user_id = playerId).first().duedate if if_playerId_exists_in_vip else datetime.now()
			duedate_after = duedate_before + time_delta
			if if_playerId_exists_in_vip:
				try:
					row = db.session.query(Vip).filter_by(user_id = playerId).first()
					row.duedate = duedate_after
					db.session.commit()
				except IndentationError as error:
					#  TODO: error handling
			else:
				row = Vip(user_id = playerId, level = 1, active = True, duedate = duedate_after)
				try:
					db.session.add(row)
					db.session.commit()
				except IntegrityError as error:
					#  TODO: error handling
			return {'result':'yes'}
		else:
			#  TODO: error handling

class apiForFinance:
	def get(self):
		# get all finance products
	
	def post(self):
		# playerId buys a financeType


activity_api.add_resource(apiForTheme, '/theme/')
activity_api.add_resource(apiForVip, '/vip/')
activity_api.add_resource(apiForFinance, '/finance/')