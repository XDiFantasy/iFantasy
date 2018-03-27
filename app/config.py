
sms_key = "24be6ffdbdc18"

BASE = "mysql+pymysql://team1:12345qwert@192.168.0.{0}:3306/team1"
READ_DATABASE = BASE.format(250)
WRITE_DATABASE = BASE.format(251)

class Config:
    pass

class DeveploeConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://team1:12345qwert@192.168.0.251:3306/'

class ReleaseConfig(Config):
    pass

config = {
    'develop':DeveploeConfig,
    'release':ReleaseConfig
}