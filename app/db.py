from flask import current_app, g
import sqlite3

# get an instance of the db
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(current_app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db

# initialize db for the first time
def init_db():
    with current_app.app_context():
        db = get_db()
        with current_app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# perform generic query, not very secure yet
def query_db(query, parameters=(), one=False):
    db = get_db()
    cursor = db.execute(query, parameters)
    rv = cursor.fetchall()
    cursor.close()
    db.commit()
    return (rv[0] if rv else None) if one else rv

# TODO: Add more specific queries to simplify code


# automatically called when application is closed, and closes db connection
def init_app(app):
    app.teardown_appcontext(close_connection)

def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()