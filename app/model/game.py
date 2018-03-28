from app import db


class GameHistory(db.Model):
    __tablename__ = "game_history"

    id = db.Column("id", db.Integer, primary_key=True)
    time = db.Column('time', db.DateTime)

    def __init__(self, time):
        self.time = time

    def __repr__(self):
        return "<GameHistory {0}, {1}>".format(self.id, str(self.time))


class UserGame(db.Model):
    __tablename__ = 'user_game'
    __table_args__ = (
        db.PrimaryKeyConstraint('user_id', 'game_history_id'),
    )
    user_id = db.Column("user_id", db.ForeignKey('user.id'))
    game_history_id = db.Column("game_history_id", db.ForeignKey('game_history.id'))

    user = db.relationship('User', backref='usergame', lazy='dynamic')

    game_history = db.relationship('GameHistory', backref='usergame', lazy='dynamic')

    def __init__(self, user_id, game_history_id):
        self.user_id = user_id
        self.game_history_id = game_history_id

    def __repr__(self):
        return "<UserGame {0}, {1}>".format(self.user_id, self.game_history_id)
