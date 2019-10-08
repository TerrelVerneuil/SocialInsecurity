from flask import current_app, g
from datetime import datetime
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

# perform query
def query_db(query, parameters=(), one=False):
    db = get_db()
    cursor = db.execute(query, parameters)
    rv = cursor.fetchall()
    cursor.close()
    db.commit()
    return (rv[0] if rv else None) if one else rv

def get_user(username):
    return query_db('SELECT * \
                     FROM Users \
                     WHERE username = ?;',
        parameters=[username], one=True)

def create_user(username, first_name, last_name, password):
    return query_db('INSERT INTO Users \
                        (username, first_name, last_name, password) \
                     VALUES(?, ?, ?, ?);',
                     parameters=(username, first_name, last_name, password))

def add_stream_content(u_id, content, filename):
    query_db('INSERT INTO Posts (u_id, content, image, creation_time) \
              VALUES(?, ?, ?, ?);', 
              parameters=(u_id, content, filename, datetime.now()))
        
def get_stream_content(u_id):
    return query_db('SELECT p.*, u.*, \
                        (SELECT COUNT(*) \
                        FROM Comments \
                        WHERE p_id=p.id) AS cc \
                    FROM Posts AS p \
                    JOIN Users AS u \
                    ON u.id=p.u_id \
                    WHERE p.u_id IN (SELECT u_id \
                                    FROM Friends \
                                    WHERE f_id=?) \
                    OR p.u_id IN (SELECT f_id \
                                    FROM Friends \
                                    WHERE u_id=?) \
                    OR p.u_id=? \
                    ORDER BY p.creation_time \
                    DESC;', parameters=[u_id, u_id, u_id])

def get_post(p_id):
    return query_db('SELECT * \
                     FROM Posts \
                     WHERE id = ?;', 
                     parameters=[p_id], one=True)

def get_comments(p_id):
    return query_db('SELECT DISTINCT * \
                     FROM Comments AS c \
                     JOIN Users AS u \
                     ON c.u_id = u.id \
                     WHERE c.p_id = ? \
                     ORDER BY c.creation_time DESC;', 
                     parameters = [p_id])

def add_comment(u_id, p_id, comment):
    query_db('INSERT INTO Comments \
                    (p_id, u_id, comment, creation_time) \
                 VALUES(?, ?, ?, ?);', 
                 parameters=(p_id, u_id, comment, datetime.now()))
   
def get_all_friends(u_id):
    return query_db('SELECT * \
                     FROM Friends AS f \
                     JOIN Users as u \
                     ON f.f_id=u.id \
                     WHERE f.u_id = ? \
                     AND f.f_id != ? ;', 
                     parameters=[u_id, u_id])

def is_user_friend(u_id, f_id):
    return query_db('SELECT * \
                     FROM Friends \
                     WHERE u_id = ? AND f_id = ?',
                     parameters=[u_id, f_id], one=True)

def add_friend(u_id, f_id):
    query_db('INSERT INTO Friends (u_id, f_id) \
              VALUES(?, ?);', 
              parameters=(u_id, f_id))

def update_profile(u_id, education, employment, music, movie, nationality, birthday):
    query_db('UPDATE Users \
              SET education=?, \
                employment=?, \
                music=?, \
                movie=?, \
                nationality=?, \
                birthday=? \
              WHERE id=? ;', 
              parameters=(education, employment, music, movie, nationality, birthday, u_id))

# automatically called when application is closed, and closes db connection
def init_app(app):
    app.teardown_appcontext(close_connection)

def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()