from app import db

#
# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/nba'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)


class VipCard(db.Model):
    __tablename__ = 'vip_card'
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=0)
    time = db.Column(db.Integer, default=0, nullable=True)
    price = db.Column(db.Integer, default=0, nullable=True)

    def __init__(self, id, time, price):
        self.id = id
        self.time = time
        self.price = price

    def __repr__(self):
        return '<User %r>' % self.id


class Theme(db.Model):
    __tablename__ = 'theme'
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=0)
    title = db.Column(db.String(255), nullable=True)
    detail = db.Column(db.String(255), nullable=True)
    price = db.Column(db.Integer, nullable=True)

    def __init__(self, id, title, detail, price):
        self.id = id
        self.title = title
        self.detail = detail
        self.price = price

    def __repr__(self):
        return '<User %r>' % self.id


class Vip(db.Model):
    __tablename__ = 'vip'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True, nullable=True)
    level = db.Column(db.Integer, nullable=True, default=0)
    active = db.Column(db.Boolean, nullable=True, default=0)
    duedate = db.Column(db.DateTime, nullable=True)

    def __init__(self, user_id, level, active, duedate):
        self.user_id = user_id
        self.level = level
        self.active = active
        self.duedate = duedate

    def __repr__(self):
        return '<User %r>' % self.user_id


class FundType(db.Model):
    __tablename__ = 'fund_type'
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=0)
    price = db.Column(db.Integer, nullable=True, default=0)
    rate = db.Column(db.Float, nullable=True, default=1)

    def __init__(self, id, price, rate):
        self.id = id
        self.price = price
        self.rate = rate

    def __repr__(self):
        return '<User %r>' % self.id


class Fund(db.Model):
    __tablename__ = 'fund'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True, nullable=False)
    fund_type_id = db.Column(db.Integer, db.ForeignKey('fund_type.id'), primary_key=True, nullable=False)

    def __init__(self, user_id, fund_type_id):
        self.user_id = user_id
        self.fund_type_id = fund_type_id

    def __repr__(self):
        return '<User %r>' % self.user_id


# class User(db.Model):
#     __tablename__ = 'user'
#     id = db.Column(db.Integer, primary_key=True)
#
#     def __init__(self, id):
#         self.id = id
#
#     def __repr__(self):
#         return '<User %r>' % self.id
