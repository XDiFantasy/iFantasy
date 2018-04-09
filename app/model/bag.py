from app import db



class BagEquip(db.Model):
    __tablename__ = "bag_equip"
    __table_args__ = (
        db.PrimaryKeyConstraint('user_id', 'equip_id'),
    )
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    equip_id = db.Column(db.Integer, db.ForeignKey('equip.id'))
    equip_type = db.Column(db.Integer, db.ForeignKey('equip.type'))
    num = db.Column(db.Integer)

    user = db.relationship("User", backref='bagequip')
    equip = db.relationship("Equip", backref='bagequip')

    def __init__(self, user_id, equip_id):
        self.user_id, self.equip_id = (user_id, equip_id)

    def __repr__(self):
        return "<BagEquip %r, %r>" % (self.user_id, self.equip_id)


# class Equip(db.Model):
#     __tablename__ = 'equip'
#     id = db.Column(db.Integer, primary_key=True)
#     #type = 1,2,3：coat,pants,shoes
#     type = db.Column(db.Integer)
#     name = db.Column(db.String(45))
#     #一件装备影响一种attr_ch
#     attr_ch_id = db.Column(db.Integer, db.ForeignKey('attr_ch.id'))
#     attr_ch = db.relationship('AttrCh', backref="equip")
#
#     def __init__(self, name, attr_ch_id):
#         self.name, self.attr_ch_id = (name, attr_ch_id)
#
#     def __repr__(self):
#         return "<Equip %r, %r, %r>" % (self.id, self.name, self.attr_ch_id)
class Equip(db.Model):
    __tablename__ = 'equip'
    id = db.Column(db.Integer, primary_key=True)
    #type = 1,2,3：coat,pants,shoes
    type = db.Column(db.Integer)
    name = db.Column(db.String(45))
    attr = db.Column(db.Integer)
    #1: pts_equip   #得分
    #2: ast_equip   #助攻
    #3: oreb_equip  #前场篮板
    #4: dreb_equip  #后场篮板
    #5: stl_equip   #抢断
    #6: blk_equip   #封盖
    #7: tov_equip   #失误
    #8: fgm_equip   #投篮命中
    #9: fga__equip  #投丢
    #10: fg3m_equip  #三分球命中

    def __repr__(self):
        return "<Equip %r, %r, %r>" % (self.id, self.name, self.attr)


class PlayerEquip(db.Model):
    __tablename__ = "player_equip"
    __table_args__ = (
        db.PrimaryKeyConstraint('user_id', 'player_id'),
    )
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    player_id = db.Column(db.Integer, db.ForeignKey("bag_player.player_id"))
    coat_id = db.Column(db.Integer)
    pants_id = db.Column(db.Integer)
    shoes_id = db.Column(db.Integer)
    pts_equip = db.Column(db.Integer)   #得分
    ast_equip = db.Column(db.Integer)   #助攻
    oreb_equip = db.Column(db.Integer)  #前场篮板
    dreb_equip = db.Column(db.Integer)  #后场篮板
    stl_equip = db.Column(db.Integer)   #抢断
    blk_equip = db.Column(db.Integer)   #封盖
    tov_equip = db.Column(db.Integer)   #失误
    fgm_equip = db.Column(db.Integer)   #投篮命中
    fga__equip = db.Column(db.Integer)  #投丢
    fg3m_equip = db.Column(db.Integer)  #三分球命中

    user = db.relationship("User", backref='playerequip')
    bag_player = db.relationship("BagPlayer", backref='playerequip')

    def __init__(self,user_id,player_id,coat_id,pants_id,shoes_id,pts_equip,ast_equip,oreb_equip,
                 dreb_equip,stl_equip,blk_equip,tov_equip,fgm_equip,fga_equip,fg3m_equip):
        self.user_id,self.player_id,self.coat_id,self.pants_id,self.shoes_id,self.pts_equip,
        self.ast_equip,self.oreb_equip,self.dreb_equip,self.stl_equip,self.blk_equip,
        self.tov_equip,self.fgm_equip,self.fga__equip,self.fg3m_equip = (
            user_id, player_id, coat_id, pants_id, shoes_id, pts_equip, ast_equip, oreb_equip,
            dreb_equip, stl_equip, blk_equip, tov_equip, fgm_equip, fga_equip, fg3m_equip
        )

    def __repr__(self):
        return "<PlayerEquip %r %r>" % (self.user_id, self.player_id)




class BagPiece(db.Model):
    __tablename__ = "bag_piece"
    __table_args__ = (
        db.PrimaryKeyConstraint('user_id', 'player_id'),
    )
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    player_id = db.Column(db.Integer, db.ForeignKey("player_base.id"))
    num = db.Column(db.Integer)

    user = db.relationship('User', backref='bagpiece')
    player_base = db.relationship('PlayerBase', backref='bagpiece')

    def __init__(self, user_id, player_id, num):
        self.user_id, self.player_id, self.num = (
            user_id, player_id, num
        )

    def __repr__(self):
        return "<BagPiece %r, %r>" % (self.user_id, self.player_id)


class Piece(db.Model):
    __tablename__ = 'piece'
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player_base.id'))
    total_num = db.Column(db.Integer)

    player = db.relationship('PlayerBase', backref='piece')

    def __init__(self, player_id, total_num):
        self.player_id, self.total_num = (player_id, total_num)

    def __repr__(self):
        return "<Piece %r, %r, %r>" % (self.id, self.player_id, self.total_num)


class BagProp(db.Model):
    __tablename__ = "bag_prop"
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True, autoincrement=False)
    fund_card_num = db.Column(db.Integer)
    exp_card_num = db.Column(db.Integer)

    user = db.relationship('User', backref='bagprop')

    def __init__(self, user_id, fund_card_num, exp_card_num):
        self.user_id, self.fund_card_num, self.exp_card_num = (
            user_id, fund_card_num, exp_card_num
        )

    def __repr__(self):
        return "<BagProp %r, %r, %r>" % (self.user_id, self.fund_card_num, self.exp_card_num)


class BagTrailCard(db.Model):
    __tablename__ = "bag_trail_card"
    __table_args__ = (
        db.PrimaryKeyConstraint('user_id', 'player_id','time'),
    )
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    player_id = db.Column(db.Integer, db.ForeignKey('player_base.id'))
    num = db.Column(db.Integer)
    time = db.Column(db.Integer)

    user = db.relationship('User', backref='bagtrailcard')
    player = db.relationship('PlayerBase', backref='bagtrailcard')

    def __init__(self, user_id, palyer_id, num, time):
        self.user_id, self.player_id, self.num, self.time = (
            user_id, palyer_id, num, time
        )

    def __repr__(self):
        return "<BagTrailCard %r, %r, %r, %r>" % (self.user_id, self.player_id, self.num, self.time)


class PropUsing(db.Model):
    __tablename__ = "prop_using"
    __table_args__ = (
        db.PrimaryKeyConstraint('user_id', 'prop_type'),
    )
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # prop_id == 0:fund_card
    # prop_id == 1:exp_card
    prop_type = db.Column(db.Integer)
    duetime = db.Column(db.DateTime)

    user = db.relationship('User', backref='propusing')

    def __init__(self, user_id, prop_type, duetime):
        self.user_id, self.prop_type, self.duetime = (
            user_id, prop_type, duetime
        )

    def __repr__(self):
        return "<PropUsing %r, %r, %r>" % (self.user_id, self.prop_type, self.duetime)
