from app import db


class UserGame(db.Model):
    __tablename__ = 'user_game'
    id = db.Column('id',db.Integer,primary_key = True)
    user_id = db.Column("user_id", db.ForeignKey('user.id'))
    time = db.Column('time', db.DateTime)

    user = db.relationship('User', backref='usergame')
    
    def __init__(self, user_id, time):
        self.user_id = user_id
        self.time = time

    def __repr__(self):
        return "<UserGame {0}, {1}>".format(self.user_id, self.time)
