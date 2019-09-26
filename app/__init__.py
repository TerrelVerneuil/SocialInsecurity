from flask import Flask, g
from config import Config
from flask_bootstrap import Bootstrap
#from flask_login import LoginManager

# create and configure app
app = Flask(__name__)
Bootstrap(app)
app.config.from_object(Config)

# setup database to close connection on teardown
from app.classes import db
db.init_app(app)

# TODO: Handle login management better, maybe with flask_login?
#login = LoginManager(app)

# initialize db if it does not exist
import os
if not os.path.exists(app.config['DATABASE']):
    db.init_db()

if not os.path.exists(app.config['UPLOAD_PATH']):
    os.mkdir(app.config['UPLOAD_PATH'])

from app import routes