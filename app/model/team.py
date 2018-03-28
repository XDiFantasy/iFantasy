
from app import db


class PlayerBase(db.Model):
    __tablename__ = 'player_base'

    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(50))
    birthday = db.Column(db.Date)
    country = db.Column(db.String(45))
    height = db.Column(db.Float)
    weight = db.Column(db.Float)
    armspan = db.Column(db.Float)
    reach_height = db.Column(db.Float)
    draft = db.Column(db.String(255))
    contract = db.Column(db.String(255))
    #season_data_id = db.Column(db.Integer, db.ForeignKey('season_data.id'))
    team_id = db.Column(db.Integer, db.ForeignKey("team_info.id"))
    cloth_num = db.Column(db.Integer)
    pos1 = db.Column(db.String(2))
    pos2 = db.Column(db.String(2))
    price = db.Column(db.Integer)
    score = db.Column(db.Integer)
    
    season = db.relationship('SeasonData',backref='playerbase')
    team = db.relationship("TeamInfo",backref='playerbase')
    
    def __init__(self, name, birthday, country, height, wieght, armspan,
                 reach_height, draft, contract,team_id,cloth_num,pos1,pos2,price,score):
        (self.name, self.birthday, self.country, self.height, self.wieght, self.armspan, 
        self.reach_height, self.draft,self.contract, self.team_id, 
        self.cloth_num, self.pos1, self.pos2,self.price, self.score ) =(name, birthday, country, 
        height, wieght, armspan,reach_height, draft, contract,
        team_id,cloth_num,pos1,pos2,price,score)
    def __repr__(self):
        return "<PlayerBase %r>" % self.id


class TeamInfo(db.Model):
    __tablename__ = 'team_info'

    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(255))
    city = db.Column(db.String(45))
    intro = db.Column(db.String(255))
    
    def __init__(self, name, city, intro):
        self.name, self.city, self.intro = (
            name, city, intro)
    def __repr__(self):
        return "<TeamInfo %r>" % self.id

class SeasonData(db.Model):
    __tablename__ = 'season_data'
    id = id = db.Column(db.Integer,primary_key=True)
    season = db.Column(db.String(15))
    is_regular = db.Column(db.Boolean)
    player_id = db.Column(db.Integer, db.ForeignKey('player_base.id'))
    player = db.relationship('PlayerBase', backref='seasondata')

    def __init__(self, season, is_regular):
        self.season, self.is_regular = (season, is_regular)
    def __repr__(self):
        return "<SeasonData %r>" %self.id
