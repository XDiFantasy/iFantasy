from flask_restful import Api, Resource, reqparse
from app import db
from app.model import User, PlayerBase, BagPlayer, BagTrailCard, BagPiece, Theme,Sim
from .message import Message
from random import choice, random
import datetime


parser = reqparse.RequestParser()
query = db.session.query
add = db.session.add
delete = db.session.delete
commit = db.session.commit
rollback = db.session.rollback

def __commit__():
    try:
        commit()
    except Exception as e:
        rollback()
        print(e)

def __toSet__(data):
    res = set()
    for item in data:
        res.add(item[0])
    return res

def __randomPick__(lists, prob):
    r = random()
    cum = 0.0
    for item, item_prob in zip(lists, prob):
        cum += item_prob
        if r < cum: break
    return item

class recommend:
    def __init__(self):
        pass

####team will win

    def update(self,sims):
        old = set(query(Sim.player_one, Sim.player_two ).all())
        new = set(sims.keys())
        part1 = old-new
        part2 = new-old
        part3 = new&old
        sp1=Sim.player_one
        sp2 = Sim.player_two
        query(Sim).filter(db.tuple_(sp1,sp2).in_(part1)).delete()
        for (p1,p2) in part2:
            add(Sim(p1,p2,sims[(p1,p2)]))
        res = query(Sim).filter(db.tuple_(sp1,sp2).in_(part3)).all()
        for item in res:
            item.sim = sims[(item.player_one,item.player_two)]
        __commit__()

    def genRate(self):
        bag_players = query(BagPlayer.user_id, BagPlayer.player_id, BagPlayer.score).all()
        scores = dict(query(PlayerBase.id, PlayerBase.score).all())
        rates = dict()
        rang = [0,0]
        for item in bag_players:
            rate = item[2]-scores[item[1]]
            rang[0] = min(rang[0],rate)
            rang[1] = max(rang[1],rate)
            if item[1] not in rates:
                rates[item[1]]={item[0]:rate}
            else:
                rates[item[1]][item[0]]=rate
        for player in rates:
            for user in rates[player]:
                rates[player][user] = (rates[player][user]-rang[0])/(rang[1]-rang[0])*9+1
        return rates

    def culcSim(self):
        rates = self.genRate()
        # sims = query(Sim.player_one,Sim.player_two).all()
        res = dict()
        for p1 in rates:
            for p2 in rates:
                if (p1,p2) in res or (p2,p1) in res:
                    continue
                res1 = res2 = res3 = 0
                for u in rates[p1]:
                    if u in rates[p2]:
                        res1 +=rates[p1][u]*rates[p2][u]
                    res2 += rates[p1][u]**2
                for u in rates[p2]:
                    res3 += rates[p2][u]**2
                if res2*res3==0:
                    continue
                cosv = res1/((res2*res3)**0.5)
                res[(p1,p2)]=cosv
        self.update(res)

    def genTrial(self,user_id):
        filter1 = query(BagPlayer.player_id).filter(BagPlayer.user_id == user_id).all()
        filter1 = __toSet__(filter1)
        filter2 = query(BagTrailCard.player_id).filter(BagTrailCard.user_id == user_id).all()
        filter2 = __toSet__(filter2)
        if self.isNewUser(user_id):
            players = self.scoreBased()
        else:
            players = self.itemBased()
        res = set(players)-filter1
        if res:
            players = res
        res = set(players) - filter2
        if res:
            players = res
        player_id = choice(players)
        time_class = [1, 3, 5]
        prob = [0.85, 0.1, 0.05]
        time = __randomPick__(time_class, prob)
        return {"id": player_id, "time": time}


    def scoreBased(self):
        pass

    def itemBased(self):
        pass

    def isNewUser(self,user_id):
        pass

    def idNewPlayer(self):
        pass


####user would like
    def calcPopular(self):
        pass

    def contentBased(self):
        pass

    def sortRecommend(self):
        pass

####optimize
    def genPiece(self):
        pass