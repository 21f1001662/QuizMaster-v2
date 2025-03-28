from flask.cli import FlaskGroup
from app import create_app, db
from flask_migrate import Migrate, MigrateCommand

cli = FlaskGroup(create_app=create_app)

@cli.command("create_db")
def create_db():
    db.create_all()

@cli.command("drop_db")
def drop_db():
    db.drop_all()

if __name__ == '__main__':
    cli() 