from app import db

class VipCard(db.Model):
    __tablename__ = 'vip_card'
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    time = db.Column(db.Integer, default=0, nullable=True)
    price = db.Column(db.Integer, default=0, nullable=True)

    def __init__(self, time, price):
        self.time = time
        self.price = price

    def __repr__(self):
        return '<VipCard %r>' % self.id


class Theme(db.Model):
    __tablename__ = 'theme'
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    title = db.Column(db.String(255), nullable=True)
    detail = db.Column(db.String(255), nullable=True)
    price = db.Column(db.Integer, nullable=True)
    player_one = db.Column(db.Integer, db.ForeignKey('player_base.id'), nullable=False)
    player_two = db.Column(db.Integer, db.ForeignKey('player_base.id'), nullable=False)
    player_three = db.Column(db.Integer, db.ForeignKey('player_base.id'), nullable=False)

    def __init__(self, title, detail, price, player_one, player_two, player_three):
        self.title = title
        self.detail = detail
        self.price = price
        self.player_one = player_one
        self.player_two = player_two
        self.player_three = player_three

    def __repr__(self):
        return '<Theme %r>' % self.id


class Vip(db.Model):
    __tablename__ = 'vip'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    level = db.Column(db.Integer, nullable=True, default=0)
    active = db.Column(db.Boolean, nullable=True, default=0)
    duedate = db.Column(db.DateTime, nullable=True)
    
    user = db.relationship('User',backref='vip')

    def __init__(self, user_id, level, active, duedate):
        self.user_id = user_id
        self.level = level
        self.active = active
        self.duedate = duedate

    def __repr__(self):
        return '<Vip %r>' % self.user_id


class FundType(db.Model):
    __tablename__ = 'fund_type'
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    price = db.Column(db.Integer, nullable=True, default=0)
    rate = db.Column(db.Float, nullable=True, default=1)

    def __init__(self,price, rate):
        self.price = price
        self.rate = rate

    def __repr__(self):
        return '<FundType %r>' % self.id


class Fund(db.Model):
    __tablename__ = 'fund'
    __table_args__ = (
        db.PrimaryKeyConstraint('user_id', 'fund_type_id'),
    )
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    fund_type_id = db.Column(db.Integer, db.ForeignKey('fund_type.id'))
    
    user  = db.relationship('User',backref='fund')
    fund_type = db.relationship('FundType', backref='fund')

    def __init__(self, user_id, fund_type_id):
        self.user_id = user_id
        self.fund_type_id = fund_type_id

    def __repr__(self):
        return '<Fund %r, %r>' % (self.user_id, self.fund_type_id)
