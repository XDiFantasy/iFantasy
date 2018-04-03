from app import db


class PlayerBase(db.Model):
    __tablename__ = 'player_base'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    birthday = db.Column(db.Date)
    country = db.Column(db.String(45))
    height = db.Column(db.Float)
    weight = db.Column(db.Float)
    armspan = db.Column(db.Float)
    reach_height = db.Column(db.Float)
    draft = db.Column(db.String(255))

    # season_data_id = db.Column(db.Integer, db.ForeignKey('season_data.id'))
    team_id = db.Column(db.Integer, db.ForeignKey("team_info.id"))
    cloth_num = db.Column(db.Integer)
    pos1 = db.Column(db.String(2))
    pos2 = db.Column(db.String(2))
    price = db.Column(db.Integer)
    score = db.Column(db.Integer)

    team = db.relationship("TeamInfo", backref='playerbase')

    def __init__(self, name, birthday, country, height, wieght, armspan,
                 reach_height, draft, team_id, cloth_num, pos1, pos2, price, score):
        (self.name, self.birthday, self.country, self.height, self.wieght, self.armspan,
         self.reach_height, self.draft, self.team_id,
         self.cloth_num, self.pos1, self.pos2, self.price, self.score) = (name, birthday, country,
                                                                          height, wieght, armspan, reach_height, draft,
                                                                          
                                                                          team_id, cloth_num, pos1, pos2, price, score)

    def __repr__(self):
        return "<PlayerBase %r>" % self.id


class TeamInfo(db.Model):
    __tablename__ = 'team_info'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    city = db.Column(db.String(45))
    intro = db.Column(db.String(255))

    def __init__(self, name, city, intro):
        self.name, self.city, self.intro = (
            name, city, intro)

    def __repr__(self):
        return "<TeamInfo %r>" % self.id


class SeasonData(db.Model):
    __tablename__ = 'season_data'
    id = db.Column(db.Integer, primary_key=True)
    season = db.Column(db.String(15))
    is_regular = db.Column(db.Boolean)
    player_id = db.Column(db.Integer, db.ForeignKey('player_base.id'))
    player = db.relationship('PlayerBase', backref='seasondata')

    def __init__(self, season, is_regular):
        self.season, self.is_regular = (season, is_regular)

    def __repr__(self):
        return "<SeasonData %r>" % self.id


class BagPlayer(db.Model):
    __tablename__ = "bag_player"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    player_id = db.Column(db.Integer, db.ForeignKey('player_base.id'))
    score = db.Column(db.Integer)
    salary = db.Column(db.Integer)
    input_data_id = db.Column(db.Integer, db.ForeignKey('input_data.id'))
    duedate = db.Column(db.DateTime)
    contract = db.Column(db.String(255))

    user = db.relationship('User', backref='bagplayer')
    player = db.relationship('PlayerBase', backref='bagplayer')
    input_data = db.relationship('InputData', backref='bagplayer')

    def __init__(self, user_id, player_id, score, salary, input_data_id, duedate,contract):
        self.user_id, self.palyer_id, self.score, self.salary, self.input_data_id, self.duedate,self.contract = (
            user_id, player_id, score, salary, input_data_id, duedate, contract
        )

    def __repr__(self):
        return "<BagPlayer %r>" % self.id


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
