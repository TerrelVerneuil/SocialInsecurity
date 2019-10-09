import os

# contains application-wide configuration, and is loaded in __init__.py

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'thisIsASecretYouWillNeverGuess!'
    DATABASE = 'database.db'
    UPLOAD_PATH = 'app/static/uploads'
    ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'svg', 'bmp']
    RECAPTCHA_PUBLIC_KEY = '6LcI4rsUAAAAAMjOMjBw-JS6vhY0Vq-JaE9Q6RQL'
    RECAPTCHA_PRIVATE_KEY = '6LcI4rsUAAAAAFGRBT30xEY9wRSFKULEOmxu0B92'