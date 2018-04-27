from flask_restful import Api, Resource, reqparse
from app import db
from app.model import User, PlayerBase, BagPlayer, BagTrailCard, BagPiece, Theme, Sim, PlayerStat, UserStat
from .message import Message
from random import choice, random
import datetime

parser = reqparse.RequestParser()
query = db.session.query
add = db.session.add
add_all = db.session.add_all
delete = db.session.delete
commit = db.session.commit
rollback = db.session.rollback


def __commit__(mes=None):
    try:
        commit()
        return mes
    except Exception as e:
        rollback()
        print(e)
        return None


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
        self.sims = None
        self.mode = None
        self.delInvalidPlayer()
        items = query(Sim.player_one, Sim.player_two, Sim.sim).all()
        if items is None:
            self.calcSim()
        else:
            self.getSim(items)
        items = query(PlayerStat.player_id, PlayerStat.mode).all()
        if items is None:
            self.genMode()
        else:
            self.mode = dict(items)
        self.player_score = dict(query(PlayerBase.id, PlayerBase.score).all())

    ####team will win

    def genTrial(self, user_id):
        filter0 = query(BagPlayer.player_id,BagPlayer.score).filter(BagPlayer.user_id == user_id).all()
        filter1 = __toSet__(filter0)
        filter2 = query(BagTrailCard.player_id).filter(BagTrailCard.user_id == user_id).all()
        filter2 = __toSet__(filter2)
        user = query(UserStat).get(user_id)
        if user is None or user.rated_num < 10:  ##判断新老用户
            players = self.scoreBased(filter1,filter2)
        else:
            players = self.itemBased(filter0,filter1,filter2)
        if not players:
            return None
        if len(players) > 20:
            players = players[:20]
        player_id = choice(players)
        time_class = [1, 3, 5]
        prob = [0.85, 0.1, 0.05]
        time = __randomPick__(time_class, prob)
        return {"id": player_id, "time": time}

    def scoreBased(self,bp,tp):  ##众数法
        if self.mode is None:
            self.genMode()
        mp = set(self.mode.keys())
        mp = mp -bp
        if mp -tp:
            mp = mp -tp
        if len(mp) < 1:
            return None
        pm = [(p,self.mode[p]) for p in self.mode if p in mp]
        pm = sorted(pm, key=lambda x:x[1],reverse = True)
        return [p for (p,r) in pm]

    def itemBased(self,bps,bp,tp,user_id):  ##项目协同
        prop = [0]*4
        for (p,s) in bps:
            if s<=70:
                prop[0]+=1
            if s>70 and s<=80:
                prop[1]+=1
            if s>80 and s<=90:
                prop[2]+=1
            if s>90:
                prop[3]+=1
        level =__randomPick__(range(4),prop)
        ud=BagPlayer.user_id
        sc=BagPlayer.score
        if level ==0:
            pl = query(BagPlayer.player_id).filter( ud== user_id,sc<=70).all()
        if level ==1:
            pl = query(BagPlayer.player_id).filter(ud == user_id, sc > 70,sc<=80).all()
        if level == 2:
            pl = query(BagPlayer.player_id).filter(ud == user_id, sc > 80, sc <= 90).all()
        if level ==3:
            pl = query(BagPlayer.player_id).filter( ud== user_id,sc>90).all()
        pl = set(pl) -bp
        if pl -tp:
            pl = pl -tp
        if len(pl) < 1:
            return None
        player_rate = [(p,s-self.player_score[p]) for (p,s) in bps]
        rates=dict([(p,0) for p in pl])
        for p in pl:
            for (b,r) in player_rate:
                rates[p]+=r*self.sims[p][b]
        pl=sorted(rates.items(), key=lambda x: x[1], reverse=True)
        return [p for (p,r) in pl]


    def calcSim(self):  ##O(P^2·U)
        rates = self.genRate()
        res = dict()
        for p1 in rates:
            for p2 in rates:
                if ((p1, p2) in res) or ((p2, p1) in res):
                    continue
                val = self.cosv(rates[p1], rates[p2])
                if val:
                    res[(p1, p2)] = val
        self.updateSim(res)

    def cosv(self, v1, v2):  ##O(U)
        res1 = res2 = res3 = 0
        for u in v1:
            if u in v2:
                res1 += v1[u] * v2[u]
            res2 += v1[u] ** 2
        for u in v2:
            res3 += v2[u] ** 2
        if res2 * res3 == 0:
            return None
        return res1 / ((res2 * res3) ** 0.5)

    def updateSim(self, sims):
        query(Sim).delete()
        add_all([Sim(item[0], item[1], sims[item]) for item in sims])
        __commit__()
        items = [(item[0], item[1], sims[item]) for item in sims]
        self.getSim(items)

    def genMode(self):
        rates = self.genRate()
        query(PlayerStat).delete()
        modes = list()
        for player in rates:
            data = [0] * 10
            for user in rates[player]:
                data[int(rates[player][user])] += 1
            mode = data.index(max(data))
            modes.append((player, mode))
        add_all([PlayerStat(p, m) for (p, m) in modes])
        __commit__()
        self.mode = dict(modes)

    def genRate(self):  ##O(U·P)
        users = query(User.id).all()
        userRatedNum = dict([(user[0], 0) for user in users])
        bag_players = query(BagPlayer.user_id, BagPlayer.player_id, BagPlayer.score).all()
        scores = self.player_score
        rates = dict()
        rang = [0, 0]
        for item in bag_players:
            rate = item[2] - scores[item[1]]
            if rate == 0:
                continue
            userRatedNum[item[0]] += 1
            rang[0] = min(rang[0], rate)
            rang[1] = max(rang[1], rate)
            if item[1] not in rates:
                rates[item[1]] = {item[0]: rate}
            else:
                rates[item[1]][item[0]] = rate
        self.updateUserStat(userRatedNum)
        for player in rates:
            for user in rates[player]:
                rates[player][user] = (rates[player][user] - rang[0]) / (rang[1] - rang[0]) * 9 + 1
        return rates

    def updateUserStat(self, userRatedNum):
        for user_id in userRatedNum:
            res = query(UserStat).get(user_id)
            if res is None:
                add(UserStat(user_id, userRatedNum[user_id], 0))
            else:
                res.rated_num = userRatedNum[user_id]
        __commit__()

    def delInvalidPlayer(self):
        now = datetime.datetime.now()
        query(BagPlayer).filter(BagPlayer.duedate <= now).delete()

    def getSim(self, items):
        players = self.player_score.keys()
        self.sims = dict([(p1, dict([(p2, 0) for p2 in players])) for p1 in players])
        for (p1, p2, sim) in items:
            self.sims[p1][p2] = sim
            self.sims[p2][p1] = sim

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
