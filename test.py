from app import create_app, db

app = create_app('develop')
db.create_all()

