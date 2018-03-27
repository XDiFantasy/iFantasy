from app import db

class BagPlayer(db.Model):
    __tablename__ = "bag_player"
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer)
    palyer_id = db.Column(db.Integer)
    score = db.Column(db.Integer)
    salary = db.Column(db.Integer)
    input_data_id = db.Column(db.Integer)
    duedate = db.Column(db.DateTime)

    def __repr__(self):
        return "<BagPlayer %r>" % self.id


class InputData(db.Model):
    __tablename__ = "input_data"
    id = db.Column(db.Integer, primary_key = True)

    def __repr__(self):
        return "<InputData %r>" % self.id

class BagEquip(db.Model):
    __tablename__ = "bag_equip"
    user_id = db.Column(db.Integer)
    equip_id = db.Column(db.Integer)
    num = db.Column(db.Integer)

    def __repr__(self):
        return "<BagEquip %r>" % self.user_id

class BagPiece(db.Model):
    __tablename__ = "bag_piece"
    user_id = db.Column(db.Integer)
    piece_id = db.Column(db.Integer)
    num = db.Column(db.Integer)

    def __repr__(self):
        return "<BagPiece %r>" % self.user_id

class BagProp(db.Model):
    __tablename__ = "bag_prop"
    user_id = db.Column(db.Integer)
    fund_card_num = db.Column(db.Integer)
    exp_card_num = db.Column(db.Integer)

    def __repr__(self):
        return "<BagProp %r>" % self.user_id

class BagTrailCard(db.Model):
    __tablename__ = "bag_trail_card"
    user_id = db.Column(db.Integer)
    player_id = db.Column(db.Integer)
    num = db.Column(db.Integer)
    time = db.Column(db.Integer)

    def __repr__(self):
        return "<BagTrailCard %r>" % self.user_id

class PropUsing(db.Model):
    __tablename__ = "prop_using"
    user_id = db.Column(db.Integer)
    prop_type = db.Column(db.Integer)
    duetime = db.Column(db.Integer)

    def __repr__(self):
        return "<PropUsing %r>" % self.user_id

