from flask import jsonify

class Message:
    '''
    {
        'error': str,
        'state':int,
        'result':None,[],{}
    }
    :state : >=0 OK, <0 error 
    '''
    def __init__(self,result=None,error='',state=0):
        self.__data = dict()
    def add(self, key, value):
        self.__data[key] = value
    def __str__(self):
        return jsonify(self.__data)


    
    
        
    