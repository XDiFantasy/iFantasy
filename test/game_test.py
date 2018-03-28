import requests
import time

gameurl = 'http://127.0.0.1:5000/api/v1/game/game'

def sendPost(user_id, token):
    data = requests.post(gameurl,data={
        'user_id':user_id,
        'token':token
    })
    print("user : "+str(user_id)+" res: "+data.text)

resulturl = 'http://127.0.0.1:5000/api/v1/gameresult/'

def getResult(user_id):
    data = requests.get(resulturl+str(user_id))

    print("user : "+str(user_id)+" res : "+data.text)

if __name__ == '__main__':
    
    sendPost(1,'haha')
    sendPost(2,'hehe')
    time.sleep(1)
    #getResult(1)
    #getResult(2)

