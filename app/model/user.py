from app import db


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(20))
    tel = db.Column(db.String(15))
    level = db.Column(db.Integer)
    money = db.Column(db.Integer)
    token = db.Column(db.String(1024))

    def __init__(self, nickname, tel, level, money):
        self.nickname, self.tel, self.level, self.money = (
            nickname, tel, level, money
        )

    def __repr__(self):
        return "<User %r>" % self.id
