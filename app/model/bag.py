from app import db


class BagPlayer(db.Model):
    __tablename__ = "bag_player"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    palyer_id = db.Column(db.Integer, db.ForeignKey('player_base.id'))
    score = db.Column(db.Integer)
    salary = db.Column(db.Integer)
    input_data_id = db.Column(db.Integer, db.ForeignKey('input_data.id'))
    duedate = db.Column(db.DateTime)

    user = db.relationship('User', backref='bagplayer', lazy='dynamic')
    player = db.relationship('PlayerBase', backref='bagplayer', lazy='dynamic')
    input_data = db.relationship('InputData', backref='bagplayer', lazy='dynamic')

    def __init__(self, user_id, player_id, score, salary, input_data_id, duedate):
        self.user_id, self.palyer_id, self.score, self.salary, self.input_data_id, self.duedate = (
            user_id, player_id, score, salary, input_data_id, duedate
        )

    def __repr__(self):
        return "<BagPlayer %r>" % self.id


class InputData(db.Model):
    __tablename__ = "input_data"
    id = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return "<InputData %r>" % self.id


class BagEquip(db.Model):
    __tablename__ = "bag_equip"
    __table_args__ = (
        db.PrimaryKeyConstraint('user_id', 'equip_id'),
    )
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    equip_id = db.Column(db.Integer, db.ForeignKey('equip.id'))

    num = db.Column(db.Integer)

    user = db.relationship("User", backref='bagequip', lazy="dynamic")
    equip = db.relationship("Equip", backref='bagequip', lazy='dynamic')

    def __init__(self, user_id, equip_id):
        self.user_id, self.equip_id = (user_id, equip_id)

    def __repr__(self):
        return "<BagEquip %r, %r>" % (self.user_id, self.equip_id)


class Equip(db.Model):
    __tablename__ = 'equip'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45))
    attr_ch_id = db.Column(db.Integer, db.ForeignKey('attr_ch.id'))

    attr_ch = db.relationship('AttrCh', backref="equip", lazy='dynamic')

    def __init__(self, name, attr_ch_id):
        self.name, self.attr_ch_id = (name, attr_ch_id)

    def __repr__(self):
        return "<Equip %r, %r, %r>" % (self.id, self.name, self.attr_ch_id)


class BagPiece(db.Model):
    __tablename__ = "bag_piece"
    __table_args__ = (
        db.PrimaryKeyConstraint('user_id', 'piece_id'),
    )
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    piece_id = db.Column(db.Integer, db.ForeignKey("piece.id"))
    num = db.Column(db.Integer)

    user = db.relationship('User', backref='bagpiece', lazy='dynamic')
    piece = db.relationship('Piece', backref='bagpiece', lazy='dynamic')

    def __init__(self, user_id, piece_id, num):
        self.user_id, self.piece_id, self.num = (
            user_id, piece_id, num
        )

    def __repr__(self):
        return "<BagPiece %r, %r>" % (self.user_id, self.piece_id)


class Piece(db.Model):
    __tablename__ = 'piece'
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player_base.id'))
    total_num = db.Column(db.Integer)

    player = db.relationship('PlayerBase', backref='piece', lazy='dynamic')

    def __init__(self, player_id, total_num):
        self.player_id, self.total_num = (player_id, total_num)

    def __repr__(self):
        return "<Piece %r, %r, %r>" % (self.id, self.player_id, self.total_num)


class BagProp(db.Model):
    __tablename__ = "bag_prop"
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True, autoincrement=False)
    fund_card_num = db.Column(db.Integer)
    exp_card_num = db.Column(db.Integer)

    user = db.relationship('User', backref='bagprop', lazy='dynamic')

    def __init__(self, user_id, fund_card_num, exp_card_num):
        self.user_id, self.fund_card_num, self.exp_card_num = (
            user_id, fund_card_num, exp_card_num
        )

    def __repr__(self):
        return "<BagProp %r, %r, %r>" % (self.user_id, self.fund_card_num, self.exp_card_num)


class BagTrailCard(db.Model):
    __tablename__ = "bag_trail_card"
    __table_args__ = (
        db.PrimaryKeyConstraint('user_id', 'player_id'),
    )
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    player_id = db.Column(db.Integer, db.ForeignKey('player_base.id'))
    num = db.Column(db.Integer)
    time = db.Column(db.Integer)

    user = db.relationship('User', backref='bagtrailcard', lazy='dynamic')
    player = db.relationship('PlayerBase', backref='bagtrailcard', lazy='dynamic')

    def __init__(self, user_id, palyer_id, num, time):
        self.user_id, self.player_id, self.num, self.time = (
            user_id, palyer_id, num, time
        )

    def __repr__(self):
        return "<BagTrailCard %r, %r, %r, %r>" % (self.user_id, self.player_id, self.num, self.time)


class PropUsing(db.Model):
    __tablename__ = "prop_using"
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    prop_type = db.Column(db.Integer)
    duetime = db.Column(db.DateTime)

    user = db.relationship('User', backref='propusing', lazy='dynamic')

    def __init__(self, user_id, prop_type, duetime):
        self.user_id, self.prop_type, self.duetime = (
            user_id, prop_type, duetime
        )

    def __repr__(self):
        return "<PropUsing %r, %r, %r>" % (self.user_id, self.prop_type, self.duetime)
