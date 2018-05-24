class OutputData:
    __colName = ['oreb','dreb','ast','stl','blk','in_pts','tov','ft','three_pt']

    def __init__(self, data):
        self.__data = {
            colName:data.get(colName) for colName in self.__colName
        }
    @property
    def data(self):
        return self.__data
    @staticmethod
    def colName():
        return OutputData.__colName
from .models import MLP4, mx, nd
