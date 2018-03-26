from flask import Flask, Blueprint, request
from flask_restful import Api, Resource, url_for

app = Flask(__name__)
api_bp = Blueprint('api', __name__)
api = Api(api_bp)

class TodoItem(Resource):
    def get(self, id):
        return {'task': 'Say "Hello, World!"'}
    def put(self,id):
        d = request.form['data']
        return {'new data':d}

api.add_resource(TodoItem, '/todos/<int:id>')
app.register_blueprint(api_bp,url_prefix='/api')

app.run(debug=True)