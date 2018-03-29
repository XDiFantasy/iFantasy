from app import db


class Recruit(db.Model):
    __tablename__ = "recruit"

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    num = db.Column(db.Integer, default=0)
    time = db.Column(db.Dateime)

    def __init__(self,user_id,num,time):
        self.user_id = user_id
        self.num = num
        self.time = time

    def __repr__(self):
        return "<Recruit %r>" % self.user_id