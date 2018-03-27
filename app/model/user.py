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
    team_id = db.Column(db.Interger, db.ForeignKey('team_info.id'))
    pf = db.Column(db.Interger, db.ForeignKey('bag_player.id'))
    c = db.Column(db.Interger, db.ForeignKey('bag_player.id'))
    sf = db.Column(db.Interger, db.ForeignKey('bag_player.id'))
    sg = db.Column(db.Interger, db.ForeignKey('bag_player.id'))
    pg = db.Column(db.Interger, db.ForeignKey('bag_player.id'))
    strategy_id = db.Column(db.Interger, db.ForeignKey('strategy.id'))

    user = db.relationship('User', backref='lineup', lazy='dynamic')
    team_info = db.relationship('TeamInfo', backref='lineup', lazy='dynamic')
    bag_player = db.relationship('BagPlayer', backref='lineup', lazy='dynamic')
    strategy = db.relationship('Strategy', backref='lineup', lazy='dynamic')

    def __init__(self, user_id, team_id, pf, c, sf, sg, pg, strategy_id):
        self.user_id, self.team_id, self.pf, self.c, self.sf, self.sg, self.pg, self.strategy_id = (
            user_id, team_id, pf, c, sf, sg, pg, strategy_id
        )

    def __repr__(self):
        return "<LineUp %r>" % self.id


class Vip(db.Model):
    __tablename__ = "vip"
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    level = db.Column(db.Integer)
    active = db.Column(db.SmallInteger)
    duedate = db.Column(db.DateTime)

    user = db.relationship('User', backref='vip', lazy='dynamic')

    def __init__(self, user_id, level, active, duedate):
        self.user_id, self.level, self.active, self.duedate = (
            user_id, level, active, duedate
        )

    def __repr__(self):
        return "<Vip %r>" % self.user_id


class VipCard(db.Model):
    __tablename__ = "vip_card"
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer)
    price = db.Column(db.Integer)

    def __init__(self, time, price):
        self.time, self.price = (
            time, price
        )

    def __repr__(self):
        return "<VipCard %r>" % self.id


class Fund(db.Model):
    __tablename__ = "fund"
    __table_args__ = (
        db.PrimaryKeyConstraint('user_id', 'fund_type_id'),
    )
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    fund_type_id = db.Column(db.Integer, db.ForeignKey('fund_type.id'))

    user = db.relationship('User', backref='fund', lazy='dynamic')
    fund_type = db.relationship('FundType', backref='fund', lazy='dynamic')

    def __init__(self, user_id, fund_type_id):
        self.user_id, self.fund_type = (
            user_id, fund_type_id
        )

    def __repr__(self):
        return "<Fund %r, %r>" % (self.user_id, self.fund_type_id)


class FundType(db.Model):
    __tablename__ = "fund_type"
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer)
    rate = db.Column(db.FLOAT)

    def __init__(self, price, rate):
        self.price, self.rate = (
            price, rate
        )

    def __repr__(self):
        return "<FundType %r>" % self.id


class Friend(db.Model):
    __tablename__ = "friend"
    __table_args__ = (
        db.PrimaryKeyConstraint('user_id', 'friend_id'),
    )
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    friend_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    user = db.relationship('User', backref='friend', lazy='dynamic')

    def __init__(self, user_id, friend_id):
        self.user_id, self.friend_id = (
            user_id, friend_id
        )

    def __repr__(self):
        return "<Friend %r, %r>" % (self.user_id, self.friend_id)
