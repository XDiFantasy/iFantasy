from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell

from app import create_app, db
from app.model import * #SeasonTheme, Vip, VipCard, Fund, FundType,BagEquip, BagPiece, BagPlayer, BagProp, PropUsing, InputData,Equip,Piece,BagTrailCard,Friend, GameHistory, UserGame,Strategy, AttrCh,PlayerBase,TeamInfo,User, LineUp

def make_shell_context():
    return dict(app=app, db=db,
    SeasonData=SeasonData,Theme=Theme, Vip = Vip, 
    VipCard = VipCard, Fund=Fund, FundType=FundType, 
    BagEquip=BagEquip, BagPlayer=BagPlayer, BagPiece=BagPiece,
    BagProp=BagProp,PropUsing=PropUsing,InputData=InputData,
    Recruit=Recruit,Equip=Equip,Piece=Piece,BagTrailCard=BagTrailCard,Friend=Friend,
    UserGame=UserGame, Strategy=Strategy,AttrCh=AttrCh, UserMatch=UserMatch,
    PlayerBase=PlayerBase,TeamInfo=TeamInfo,User=User, LineUp=LineUp
    )

app = create_app("develop")
manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

manager.add_command("shell", Shell(make_context=make_shell_context))

if __name__ == "__main__":
    manager.run()
    # user1 = User('user1','120',1,1200)
    # user2 = User('user2','110',1,1200)
    # user1.token = 'debug'
    # user2.token = 'debug'
    # db.session.add_all([user1,user2])
    # db.session.commit()

    # team = TeamInfo('Team','xian','niubi')
    # db.session.add(team)
    # db.session.commit()
    # import datetime
    # players = []
    # for i in range(5):
    #     player = PlayerBase('player '+str(i),datetime.datetime.date(datetime.datetime.now()),
    #     'China',1.80,100,2.3,2.5,"draft ",team.id,12,'c',None,
    #     1000,500
    #     )
    #     players.append(player)
    # db.session.add_all(players)
    # db.session.commit()
    # inputdata = InputData()
    # att = AttrCh()
    # db.session.add_all([inputdata,att])
    # db.session.commit()
    # s = [att.id]*10
    # s = Strategy(*s)
    # db.session.add(s)
    # db.session.commit()
    # lineups = []
    # for user in [user1, user2]:
    #     db.session.add(UserMatch(user.id))
    #     db.session.commit()
    #     bagPlayers = []
    #     for player in players:
    #         bagPlayers.append(BagPlayer(user.id, player.id, player.score,player.price,
    #         inputdata.id, datetime.datetime.now()+datetime.timedelta(days=1),
    #         'contract'
    #         ))
    #     db.session.add_all(bagPlayers)
    #     db.session.commit()
            
    #     lineups.append(LineUp(user.id, team.id, bagPlayers[0].id,
    #     bagPlayers[1].id, bagPlayers[2].id,bagPlayers[3].id,
    #     bagPlayers[4].id,s.id))
    # db.session.add_all(lineups)
    # db.session.commit()
