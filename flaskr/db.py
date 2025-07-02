import sqlite3
from datetime import datetime
import click 
from flask import current_app, g

def get_db():
    if 'db' not in g:
        # used to store data that might be accessed by multiple functions
        # here the connectin is being stored in the g
        g.db = sqlite3.connect(
            # points to the flask app handling the request
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )

        # returns rows that behave like dicts
        g.db.row_factory = sqlite3.Row

    return g.db

# checks if a connection was creatd by checking if g.db was set
def close_db(e=None):
    db = g.pop('db', None)

    # if there is connection, close it
    if db is not None:
        db.close()

# handle the sql commands to the db.py file
def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

@click.command('init-db')
def init_db_command():
    """clear the existing data and create new tables"""
    init_db()
    click.echo('Initialized the database.')

sqlite3.register_converter(
    "timestamp", lambda v: datetime.fromisoformat(v.decode())
)

def init_app(app):
    # tells flask to call that function when cleaning up after returning the response
    app.teardown_appcontext(close_db)

    # adds a new command that can be called with the `flask` command
    app.cli.add_command(init_db_command)