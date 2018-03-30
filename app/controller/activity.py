from flask import Blueprint, jsonify
from flask_restful import Api, Resource
from app.model import Theme, VipCard

activity_bp = Blueprint('activity_bp', __name__)
activity_api = Api(activity_bp)


# your code
class apiForTheme(Resource):
	def get(self):
		rows = Theme.query.all()
		data = list()
		for row in rows:
			data.append({'id':row.id,'title':row.title, 'detial':row.detail, 'price':row.price})
		res = {'length':len(rows),'items':data}
		return jsonify(res)

class apiForVip(Resource):
	def get(self):
		res = dict()
		card_type = ['week','month','year','permanent']
		duration = [7,30,365,9999]
		for card in card_type:
			index = card_type.index(card)
			res[card] = VipCard.query.filter_by(time=duration[index]).first().price
		return jsonify(res)

activity_api.add_resource(apiForVip,'/vip/')
activity_api.add_resource(apiForTheme,'/theme/')