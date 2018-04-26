from flask_restful import Api, Resource, reqparse
from app import db
from app.model import User, PlayerBase, BagPlayer, BagTrailCard, BagPiece, Theme,Sim
from .message import Message
from random import choice, random
import datetime


parser = reqparse.RequestParser()
query = db.session.query
add = db.session.add
commit = db.session.commit
rollback = db.session.rollback

def __commit__():
    try:
        commit()
    except Exception as e:
        rollback()
        print(e)

class recommend:
    # def getRate(self):
    #     bag_players = query(BagPlayer.user_id,BagPlayer.player_id,BagPlayer.score).all()
    #     scores = dict(query(PlayerBase.id,PlayerBase.score).all())
    #     for item in bag_players:
    #         add(Rate(item[0],item[1],item[2]-scores[item[1]]))
    #     __commit__()

    def culcSim(self):
        bag_players = query(BagPlayer.user_id, BagPlayer.player_id, BagPlayer.score).all()
        scores = dict(query(PlayerBase.id, PlayerBase.score).all())
        rates = dict()
        for item in bag_players:
            if item[1] not in rates:
                rates[item[1]]={item[0]:item[2]-scores[item[0]]}
            else:
                rates[item[1]][item[0]]=item[2]-scores[item[0]]
        exist = list()
        for p1 in rates:
            exist.append((p1, p1))
            for p2 in rates:
                if (p1,p2) in exist:
                    continue
                res1 = res2 = res3 = 0
                for u in rates[p1]:
                    if u in rates[p2]:
                        res1 +=rates[p1][u]*rates[p2][u]
                    res2 += rates[p1][u]**2
                for u in rates[p2]:
                    res3 += rates[p2][u]**2
                cosv = res1/((res2*res3)**0.5)
                exist.append((p1,p2))
                exist.append((p2,p1))
                add(Sim(p1,p2,cosv))
                add(Sim(p2, p1, cosv))
        __commit__()



