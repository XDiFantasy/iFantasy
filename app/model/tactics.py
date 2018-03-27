from app import db

class Strategy(db.modle):
    __tablename__ = "strategy"
    id = db.Column(db.Interger,primary_key = True)
    sg = db.Column(db.Interger)
    pg = db.Column(db.Interger)
    sf = db.Column(db.Interger)
    pf = db.Column(db.Interger)
    c =db.Column(db,Interger)
    v_sg = db.Column(db.Interger)
    v_pg = db.Column(db.Interger)
    v_sf = db.Column(db.Interger)
    v_pf = db.Column(db.Interger)
    v_c = db.Column(db.Interger)from app import db
