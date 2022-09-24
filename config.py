import os      
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
# contains application-wide configuration, and is loaded in __init__.py

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret' # TODO: Use this with wtforms
    DATABASE = 'database.db'
    UPLOAD_PATH = 'app/static/uploads'
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'} # Might use this at some point, probably don't want people to upload any file type
    app = Flask(__name__)
    app.config['UPLOAD_PATH'] = UPLOAD_PATH
