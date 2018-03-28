from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell

from app import create_app, db

def make_shell_context():
    return dict(app=app, db=db)

app = create_app("develop")
manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

manager.add_command("shell", Shell(make_context=make_shell_context))

if __name__ == "__main__":
    manager.run()
