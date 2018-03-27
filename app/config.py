
sms_key = "24be6ffdbdc18"

BASE = "mysql+pymysql://team1:12345qwert@192.168.0.{0}:3306/team1"
READ_DATABASE = BASE.format(250)
WRITE_DATABASE = BASE.format(251)

class Config:
    SECRET_KEY = "miyao"
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:123456@localhost:3306/nba" #WRITE_DATABASE

class DeveploeConfig(Config):
    DEBUG = True
    

class ReleaseConfig(Config):
    DEBUG=False

config = {
    'develop':DeveploeConfig,
    'release':ReleaseConfig
}