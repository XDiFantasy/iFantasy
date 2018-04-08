from manage import *
import datetime
import random


class TestData:
    num_users = 10
    num_player = 10
    num_team = 2

    def __init__(self):
        self.users = []
        self.players = []
        self.teams = []
        self.pos = ['sg','sf','pg','pf','c']
        self.players_pos = {
            'sg':[],'sf':[],'pg':[],'pf':[],'c':[]
        }
        self.strategies = Strategy.query.all()
    def writeUser(self):
        if len(self.users) == 0:
            self.generateUsers()
        if self.users[0].id is None:
            db.session.add_all(self.users)
            db.session.commit()
    def writeTeam(self):
        if len(self.teams) == 0:
            self.genTeams()
        if self.teams[0].id is None:
            db.session.add_all(self.teams)
            db.session.commit()
    def writePlayer(self):
        if len(self.players) == 0:
            self.genPlayerBase()
        if self.players[0].id is None:
            db.session.add_all(self.players)
            db.session.commit()
    def genNicknames(self):
        for index in range(self.num_users):
            yield 'User {0}'.format(index)
    # def randPickPlayerByPos(self,pos):
    #     return self.players_pos[pos][random.randint(0,len(self.players_pos[pos])-1)]
    # def randPickTeam(self):
    #     return self.teams[random.randint(0,len(self.teams)-1)]
    # def randPickStrategy(self):
    #     return self.strategies[random.randint(0,len(self.strategies)-1)]
    def generateUsers(self):
        nicknames = self.genNicknames()
        for nickname in nicknames:
            user = User(nickname,'15000000000',1,1000,'debug','debug')
            self.users.append(user)
    def genTeams(self):
        for index in range(self.num_team):
            self.teams.append(TeamInfo('Team '+str(index),'Xi\'An','intro ...'))
    def genPlayerBase(self):
        self.writeTeam()
        for index in range(self.num_player):
            player = PlayerBase('Player '+str(index), datetime.datetime.today(),'China',1.80,180,2.3,2.5,
                'draft',self.teams[random.randint(0,len(self.teams)-1)].id,10,self.pos[index%5],None,100,100)
            self.players_pos[player.pos1].append(player)
            self.players.append(player)
    # def genLineup(self):
    #     writeUser()
    #     writeTeam()
    #     writePlayer()
    #     for user in self.users:
    #         for index in range(self.num_lineup):
    #             lineup = LineUp(user.id,self.randPickTeam().id,
    #             self.randPickPlayerByPos('pf').id,
    #             self.randPickPlayerByPos('c').id,
    #             self.randPickPlayerByPos('sf').id,
    #             self.randPickPlayerByPos('sg').id,
    #             self.randPickPlayerByPos('pg').id,
    #             self.randPickStrategy().id
    #                 )
    #             db.session.add(lineup)
    #     db.session.commit()
    # def 

if __name__ == '__main__':
    testData = TestData()
    #testData.writeUser()
    #testData.writeTeam()
    testData.writePlayer()
        
    
            

    

