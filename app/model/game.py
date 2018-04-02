from app import db


class UserGame(db.Model):
    __tablename__ = 'user_game'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    id = db.Column('id',db.Integer,primary_key = True)
    user_id = db.Column("user_id", db.ForeignKey('user.id'))
    time = db.Column('time', db.DateTime)

    pts = db.Column('pts',db.Integer)
    oreb = db.Column('oreb', db.FLOAT)
    dreb = db.Column('dreb',db.FLOAT)
    ast = db.Column(db.FLOAT)
    stl = db.Column(db.FLOAT)
    blk = db.Column(db.FLOAT)
    in_pts = db.Column(db.FLOAT)
    tov = db.Column(db.FLOAT)
    ft = db.Column(db.FLOAT)
    three_pt = db.Column(db.FLOAT)

    user = db.relationship('User', backref='usergame')
    
    def __init__(self, user_id, time, pts ,oreb, dreb, ast, stl, blk, in_pts, tov, ft, three_pt):
        self.user_id = user_id
        self.time = time
        (self.pts, self.oreb, self.dreb, self.ast, 
        self.stl, self.blk, self.in_pts, self.tov,
        self.ft, self.three_pt) = (
            pts, oreb, dreb, ast, stl, blk, in_pts, tov, ft, three_pt
        )

    def __repr__(self):
        return "<UserGame {0}, {1}>".format(self.user_id, self.time)

class UserMatch(db.Model):
    __tablename__ = 'user_match'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),primary_key=True)
    score = db.Column(db.FLOAT,default=1000)

    user = db.relationship('User', backref='usermatch')
    def __repr__(self):
        return "<UserMatch %r, %r>" % (self.user_id, self.score)
