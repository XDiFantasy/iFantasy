from flask import Blueprint
from flask_restful import abort, Api, Resource, fields, marshal_with, reqparse
from app import db
from app.model import Recruit

recruit_bp = Blueprint('recruit_bp', __name__)
recruit_api = Api(recruit_bp)
parser = reqparse.RequestParser()

def abort_if(todo_id):
    if False:
        abort(404, message="".format())



class GetRecruit(Resource):
    def get(self)):
        parser.add_argument()
        db.session.query(Recruit).filter_by(name='ed').first()


recruit_api.add_resource(GetRecruit,'/get_recruit_info')
recruit_api.add_resource(OneRecruit,'/one_recruit')
recruit_api.add_resource(FiveRecruie,'/five_recruit')
recruit_api.add_resource(RecruitPlayer,'/recruit')
recruit_api.add_resource(ShowPlayer,'/show_all_payer')