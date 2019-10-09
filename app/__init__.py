from flask import Flask, g
from config import Config
from flask_bootstrap import Bootstrap
from datetime import timedelta
from flask_login import LoginManager

# create and configure app
app = Flask(__name__)
Bootstrap(app)
app.config.from_object(Config)

# init login manager
login_manager = LoginManager()
login_manager.login_view = "index"
login_manager.init_app(app)

# setup database to close connection on teardown
from app import db
db.init_app(app)

# initialize db if it does not exist
import os
if not os.path.exists(app.config['DATABASE']):
    db.init_db(app)

if not os.path.exists(app.config['UPLOAD_PATH']):
    os.mkdir(app.config['UPLOAD_PATH'])

from app import routes