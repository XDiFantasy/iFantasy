
from app import db

# 球员基本信息
class PlayerBase(db.Model):
    __tablename__ = 'player_base'

    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(50))
    birthday = db.Column(db.DateTime)
    country = db.Column(db.String(45))
    height = db.Column(db.Float)
    weight = db.Column(db.Float)
    armspan = db.Column(db.Float)
    reach_height = db.Column(db.Float)
    draft = db.Column(db.String(255))
    contract = db.Column(db.String(255))
    season_id = db.Column(db.Integer)
    team_id = db.Column(db.Integer)
    cloth_num = db.Column(db.Integer)
    pos1 = db.Column(db.String(2))
    pos2 = db.Column(db.String(2))
    price = db.Column(db.Integer)
    score = db.Column(db.Integer)


# 球队信息
class TeamInfo(db.Model):
    __tablename__ = 'team_info'

    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(255))
    city = db.Column(db.String(45))
    intro = db.Column(db.String(255))
