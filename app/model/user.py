from app import db


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(20))
    tel = db.Column(db.String(15))
    level = db.Column(db.Integer)
    money = db.Column(db.Integer)

    def __init__(self, nickname, tel, level, money):
        self.nickname, self.tel, self.level, self.money = (
            nickname, tel, level, money
        )

    def __repr__(self):
        return "<User %r>" % self.id


class LineUp(db.Model):
    __tablename__ = "lineup"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    team_id = db.Column(db.Integer, db.ForeignKey('team_info.id'))
    pf = db.Column(db.Integer, db.ForeignKey('bag_player.id'))
    c = db.Column(db.Integer, db.ForeignKey('bag_player.id'))
    sf = db.Column(db.Integer, db.ForeignKey('bag_player.id'))
    sg = db.Column(db.Integer, db.ForeignKey('bag_player.id'))
    pg = db.Column(db.Integer, db.ForeignKey('bag_player.id'))
    strategy_id = db.Column(db.Integer, db.ForeignKey('strategy.id'))

    user = db.relationship('User', backref='lineup' )
    team_info = db.relationship('TeamInfo', backref='lineup' )

    strategy = db.relationship('Strategy', backref='lineup')

    def __init__(self, user_id, team_id, pf, c, sf, sg, pg, strategy_id):
        self.user_id, self.team_id, self.pf, self.c, self.sf, self.sg, self.pg, self.strategy_id = (
            user_id, team_id, pf, c, sf, sg, pg, strategy_id
        )

    def __repr__(self):
        return "<LineUp %r>" % self.id


