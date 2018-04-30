from app import db
from app.model import User, PlayerBase, BagPlayer, BagTrailCard, Sim, PlayerStat, UserStat,SeasonData,Like
from random import choice, random
import datetime

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


class Recommend:
    def __init__(self):
        self.__sims = None ##dict(dict())
        self.__likes = None ##dict(dict())
        self.__mode = dict()
        self.__delInvalidPlayer__()
        self.__player_score = dict(query(PlayerBase.id, PlayerBase.score).all())
        items = query(Sim.player_one, Sim.player_two, Sim.sim).all()
        if items is None:##system first init reommendation
            self.genSim()
        else:
            self.__getSim__(items)## first time all zero
            
        items = query(PlayerStat.player_id, PlayerStat.mode).all()
        self.__getMode__(items)## first time all zero
        
        items=query(UserStat.user_id,UserStat.rated_num).all()
        self.__newPlayer=dict(items)##first time none

        items = query(Like.player_one, Like.player_two, Like.like).all()
        if items is None:##system first init reommendation
            self.genLikes()
        else:
            self.__getLike__(items)

    ####team will win

    def genTrial(self, user_id):
        filter0 = query(BagPlayer.player_id,BagPlayer.score).filter(BagPlayer.user_id == user_id).all()
        filter1 = __toSet__(filter0)
        filter2 = query(BagTrailCard.player_id).filter(BagTrailCard.user_id == user_id).all()
        filter2 = __toSet__(filter2)
        if self.__isNewUser__(user_id):  ##判断新老用户
            players = self.__scoreBased__(filter1,filter2)
        else:
            players = self.__itemBased__(filter0,filter1,filter2)
        if not players:
            return None
        if len(players) > 20:
            players = players[:20]
        player_id = choice(players)
        time_class = [1, 3, 5]
        prob = [0.85, 0.1, 0.05]
        time = __randomPick__(time_class, prob)
        return {"id": player_id, "time": time}

    def __scoreBased__(self,bp,tp):  ##众数法 O(P·ln(P))
        mp = set(self.__mode.keys())
        mp = mp -bp
        if mp -tp:
            mp = mp -tp
        if len(mp) < 1:
            return None
        pm = [(p,self.__mode[p]) for p in self.__mode if p in mp]
        pm = sorted(pm, key=lambda x:x[1],reverse = True)
        return [p for (p,r) in pm]

    def __itemBased__(self,bps,bp,tp,user_id):  ##项目协同 O(P^2)
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
        player_rate = [(p,s-self.__player_score[p]) for (p,s) in bps]
        rates=dict([(p,0) for p in pl])
        for p in pl:
            for (b,r) in player_rate:
                rates[p]+=r*self.__sims[p][b]
        pl=sorted(rates.items(), key=lambda x: x[1], reverse=True)
        return [p for (p,r) in pl]

    def genSim(self):  ##O(P^2·U)
        rates = self.calcRate()
        sims = dict()
        for p1 in rates:
            for p2 in rates:
                if ((p1, p2) in sims) or ((p2, p1) in sims):
                    continue
                val = self.__cosDict__(rates[p1], rates[p2])
                if val:
                    sims[(p1, p2)] = val
        ####update sims
        query(Sim).delete()
        items = [(item[0], item[1], sims[item]) for item in sims]
        add_all([Sim(item[0], item[1], item[2]) for item in items])
        __commit__()
        self.__getSim__(items)
        self.genMode(rates)

    def genMode(self,rates = None):
        if rates is None:
            rates = self.calcRate()
        for item in query(PlayerStat).all():
            item.mode = 0
        modes = list()
        for player in rates:
            data = [0] * 10
            for user in rates[player]:
                data[int(rates[player][user])] += 1
            mode = data.index(max(data))
            modes.append((player,mode))
            query(PlayerStat).get(player).mode=mode
        __commit__()
        items = query(PlayerStat.player_id, PlayerStat.mode).all()
        self.__getMode__(items)

    def calcRate(self):  ##O(U·P)
        users = query(User.id).all()
        userRatedNum = dict([(user[0], 0) for user in users])
        bag_players = query(BagPlayer.user_id, BagPlayer.player_id, BagPlayer.score).all()
        scores = self.__player_score
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
        self.__updateUserStat__(userRatedNum)
        for player in rates:
            for user in rates[player]:
                rates[player][user] = (rates[player][user] - rang[0]) / (rang[1] - rang[0]) * 9 + 1
        return rates

    def __updateUserStat__(self, userRatedNum):
        query(UserStat).delete()
        data = list()
        for user_id in userRatedNum:
            data.append(UserStat(user_id, userRatedNum[user_id]))
        add_all(data)
        __commit__()

    def __getSim__(self, items):
        players = self.__player_score.keys()
        self.__sims = dict([(p1, dict([(p2, 0) for p2 in players])) for p1 in players])
        for (p1, p2, sim) in items:
            self.__sims[p1][p2] = sim
            self.__sims[p2][p1] = sim

    def __getMode__(self,items):
        for (p,m,po) in items:
            self.__mode[p]=m
        for pd in set(self.__player_score.keys())-__toSet__(items):##init every player_stat
            add(PlayerStat(pd,0,0))
            self.__mode[p] = 0    ##every player has mode

    def __delInvalidPlayer__(self):
        now = datetime.datetime.now()
        query(BagPlayer).filter(BagPlayer.duedate <= now).delete()

    def __cosDict__(self, v1, v2):  ##O(U)
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

    def __isNewUser__(self,user_id):
        if user_id in self.__newPlayer:
            if self.__newPlayer[user_id]>10:
                return True
        return False

    ####user would like
    def sortRecommend(self,user_id):
        if self.__isNewUser__(user_id):  ##判断新老用户
            players = self.__popularBased__()
        else:
            players = self.__contentBased__(user_id)
        return players

    def __contentBased__(self,user_id):##O(P^2)
        bag_players = query(BagPlayer.player_id).filter(BagPlayer.user_id==user_id).all()
        trial_players = query(BagTrailCard.player_id).filter(BagTrailCard.user_id==user_id).all()
        players = list()
        for player in set(self.__player_score.keys())-set(bag_players):
            score = 0
            for bp in bag_players:
                ps = self.__player_score[player]
                bps = self.__player_score[bp]
                like = self.__likes[player][bp]
                if bps>ps and bps<ps+5 and like>0.6:
                    like = like*2
                score+=like
            if player in trial_players:
                score = score*1.2
            players.append((player,score))
        for player in bag_players:
            players.append((player, 0))
        players = sorted(players, key=lambda x:x[1],reverse = True)
        return [p for (p,s) in players]

    def __popularBased__(self):
        pp = dict(query(PlayerStat.player_id,PlayerStat.popular).all())
        ppo = list()
        for p in query(PlayerBase).all():
            if p not in pp:
                pp[p] = 0
            ppo.append((p,pp[p]))
        ppo = sorted(ppo, key=lambda x:x[1],reverse = True)
        return [p for (p,po) in ppo]

    def genLikes(self):
        s = SeasonData
        players = query(s.player_id,s.gp,s.min,s.reb,s.fg_pct,s.fg3_pct,s.ft_pct,s.pts,s.ast,s.oreb,s.dreb,s.stl,s.blk,
                      s.tov,s.fgm,s.fga,s.fg3m,s.efg_pct,s.ts_pct,s.ortg,s.drtg).all()
        likes=dict()
        for p1 in players:
            for p2 in players:
                if ((p1, p2) in likes) or ((p2, p1) in likes):
                    continue
                val=self.__cosList__(p1[1:],p2[1:])
                likes[(p1[0],p2[0])]=val
        ####update likes
        query(Like).delete()
        items = [(item[0], item[1], likes[item]) for item in likes]
        add_all([Like(item[0], item[1], item[2]) for item in items])
        __commit__()
        self.__getLike__(items)

    def __getLike__(self,items):
        players = self.__player_score.keys()
        self.__sims = dict([(p1, dict([(p2, 0) for p2 in players])) for p1 in players])
        for (p1, p2, like) in items:
            self.__likes[p1][p2] = like
            self.__likes[p2][p1] = like

    def __cosList__(self, v1, v2):  ##O(U)
        res1 = res2 = res3 = 0
        if len(v1)!=len(v2):
            return None
        for i in range(len(v1)):
            res1+=v1[i]*v2[i]
            res2+=v1[i]**2
            res3+=v2[i]**2
        if res2 * res3 == 0:
            return 0
        return res1 / ((res2 * res3) ** 0.5)

    ####optimize
    def genPiece(self):
        player_id = BagPlayer.player_id
        pc = query(player_id,db.func.count(player_id)).group_by(player_id).all()
        old_players=set([p for (p,c) in pc])
        all_players=set([p for (p,s) in self.__player_score])
        players=all_players-old_players
        if not players:
            players = sorted(old_players, key=lambda x:x[1])
            if len(players)>10:
                players = players[:10]
        player_id = choice(list(players))
        num_class = [1, 5, 10, 15]
        prob = [0.45, 0.4, 0.1, 0.05]
        num = __randomPick__(num_class, prob)
        return {"id": player_id, "num": num}