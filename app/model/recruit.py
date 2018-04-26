from app import db


class Recruit(db.Model):
    __tablename__ = "recruit"

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    num = db.Column(db.Integer, default=0)
    time = db.Column(db.DateTime)
    
    user = db.relationship('User',backref='recruit')

    def __init__(self,user_id,num,time):
        self.user_id = user_id
        self.num = num
        self.time = time

    def __repr__(self):
        return "<Recruit %r>" % self.user_id

# class Rate(db.Model):
#     __tablename__ = "rate"
#
#     id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     player_id = db.Column(db.Integer, db.ForeignKey('player_base.id'), nullable=False)
#     score = db.Column(db.FLOAT)
#
#     def __init__(self,user_id,player_id,score):
#         self.user_id=user_id
#         self.player_id=player_id
#         self.score=score
#
#     def __repr__(self):
#         return "<Rate %r, %r>" % (self.user_id,self.player_id)


class Sim(db.Model):
    __tablename__ = "sim"

    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    player_one = db.Column(db.Integer, db.ForeignKey('player_base.id'), nullable=False)
    player_two = db.Column(db.Integer, db.ForeignKey('player_base.id'), nullable=False)
    sim = db.Column(db.FLOAT)

    def __init__(self,player_one,player_two,sim):
        self.player_one=player_one
        self.player_two=player_two
        self.sim=sim

    def __repr__(self):
        return "<Sim %r, %r>" % (self.player_one,self.player_two)
