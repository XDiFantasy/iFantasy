from app import db

class GameHistory(db.Model):
    __tablename__ = "game_history"

    id = db.Column("id",db.Integer, primary_key=True)
    time = db.Column('time', db.DateTime)

    def __init__(self,time):
        self.time = time
    def __repr__(self):
        return "<{0}, {1}>".format(self.id,str(self.time))

class UserGame(db.Model):
    __tablename__ = 'user_game'

    user_id = db.Column("user_id", db.ForeignKey('user.id'),autoincrement=False,primary_key=True)
    game_history_id = db.Column("game_history_id", db.ForeignKey('game_history.id'))

    game_history = db.relationship('game_history',backref='usergame',lazy='dynamic')
    
    def __init__(self, user_id, game_history_id):
        self.user_id = user_id
        self.game_history_id = game_history_id
    def __repr__(self):
        return "<{0}, {1}>".format(self.user_id, self.game_history_id)
