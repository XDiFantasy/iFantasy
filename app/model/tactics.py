from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:123456@127.0.0.1:3306/strategy"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

db = SQLAlchemy(app)

class Strategy(db.modle):
    __tablename__ = "strategy"
    id = db.Column(db.Interger,primary_key = True)
    sg = db.Column(db.Interger)
    pg = db.Column(db.Interger)
    sf = db.Column(db.Interger)
    pf = db.Column(db.Interger)
    c =db.Column(db,Interger)
    v_sg = db.Column(db.Interger)
    v_pg = db.Column(db.Interger)
    v_sf = db.Column(db.Interger)
    v_pf = db.Column(db.Interger)
    v_c = db.Column(db.Interger)