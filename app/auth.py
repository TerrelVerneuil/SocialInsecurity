from flask_login import AnonymousUserMixin, UserMixin
from argon2 import PasswordHasher
from app.db import query_db

ph = PasswordHasher()

def hash_password(password):
    return ph.hash(password)


def check_password(db_pass, password):
    try:
        return ph.verify(db_pass, password)
    except:
        return False
    

# user class, needed for flask-login to work
class User(UserMixin):
    def __init__(self, user):
        self.id = user['id']
        self.username = user['username']

    @staticmethod
    def get(id):
        user = query_db('SELECT * FROM Users WHERE id=?;',parameters=(id,), one=True)
        if user == None:
            return AnonymousUserMixin()
        return User(user)