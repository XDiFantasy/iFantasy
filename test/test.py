from flask import Flask, request

app = Flask(__name__)


@app.route("/api/v1/login", methods=['POST'])
def login():
    phone = request.get_json().get('phone')
    zone = request.get_json().get('zone')
    code = request.get_json().get('code')


api.add_resource(TodoItem, '/todos/<int:id>')
app.register_blueprint(api_bp, url_prefix='/api')

app.run(debug=True)