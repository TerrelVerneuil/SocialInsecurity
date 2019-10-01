from flask_login import AnonymousUserMixin, UserMixin
from argon2 import PasswordHasher
from app.db import query_db

ph = PasswordHasher()

def hash_password(password):
    return ph.hash(password)


# def check_password(password, email):
#     with ConnectionInstance() as queries:
#         try:
#             return ph.verify(queries.get_pass_hash(email), password)
#         except exceptions.VerifyMismatchError:
#             return False



# def get_user_id(email):
#     with ConnectionInstance as queries:
#         return queries.getUserId(email)


# user class, needed for flask-login to work
class User(UserMixin):
    def __init__(self, id):
        self.id = id
        self.username = 'test'

    @staticmethod
    def get(id):
        user = query_db('SELECT * FROM Users WHERE id=?;',parameters=(id,), one=True)
        if user == None:
            return AnonymousUserMixin()
        return User(id)