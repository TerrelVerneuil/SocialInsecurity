from flask import Flask, g, redirect, url_for, session
from config import Config
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_manager, UserMixin
from werkzeug.exceptions import RequestEntityTooLarge
import sqlite3
import os
import re
from datetime import timedelta

# create and configure app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=90)
app.config['REMEMBER_COOKIE_SECURE'] = True
app.config['SESSION_EXPIRE_AT_BROWSER_CLOSE'] = True
Bootstrap(app)
app.config.from_object(Config)

@app.errorhandler(RequestEntityTooLarge)
def handle_bad_request(e):
    return 'Too large file!', 413

SECRET_KEY = os.urandom(16)

# get an instance of the db
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db

# initialize db for the first time
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# perform generic query, not very secure yet
def query_db(query, one=False):
    db = get_db()
    cursor = db.execute(query)
    rv = cursor.fetchall()
    cursor.close()
    db.commit()
    return (rv[0] if rv else None) if one else rv

def get_user(username):
    if(re.match('^[A-Za-z0-9_-]{3,16}$', username)):
        return query_db('SELECT * FROM Users WHERE username="{}";'.format(username), one=True)
    return None

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'
login_manager.session_protection = "strong"

class User(UserMixin):
    def get_id(self):
        return self.username
    def get_idNum(self):
        return self.id

@login_manager.user_loader
def user_loader(username):
    u = get_user(username)
    user = User()
    user.username = username
    user.id = u['id']
    user.password = u['password']
    user.firstname = u['first_name']
    user.lastname = u['last_name']
    return user

@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('index'))

# automatically called when application is closed, and closes db connection
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# initialize db if it does not exist
if not os.path.exists(app.config['DATABASE']):
    init_db()

if not os.path.exists(app.config['UPLOAD_PATH']):
    os.mkdir(app.config['UPLOAD_PATH'])

from app import routes
