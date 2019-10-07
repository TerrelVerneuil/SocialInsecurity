from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, login_required, current_user
from app import app, login_manager
import app.db as db
from app.auth import User, hash_password, check_password
from app.forms import IndexForm, PostForm, FriendsForm, ProfileForm, CommentsForm
from datetime import datetime
import os

# this file contains all the different routes, and the logic for communicating with the database

# needed for flask-login to work properly
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# home page/login/registration
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    # logout first in case we are logged in
    logout_user()
    form = IndexForm()
   
    # POST
    # login
    if form.login.validate_on_submit():
        user = db.get_user(form.login.username.data)
        if check_password(user['password'], form.login.password.data):
            login_user(User(user))
            return redirect(url_for('stream', username=form.login.username.data))
        else:
            flash('Invalid username or password!')

    # register
    elif form.register.validate_on_submit():
        db.create_user(form.register.username.data, 
                       form.register.first_name.data, 
                       form.register.last_name.data, 
                       hash_password(form.register.password.data))
        flash('successfully created {} as username'.format(form.register.username.data))
        return redirect(url_for('index'))

    # GET
    return render_template('index.html', title='Welcome', form=form)

# content stream page
@app.route('/stream/<username>', methods=['GET', 'POST'])
@login_required
def stream(username):
    # redirect if someone tries to access other peoples homepage
    if not current_user.username == username:
        return redirect(url_for('stream', username=current_user.username))
    
    # POST: add new stream content
    form = PostForm()
    if form.is_submitted():
        if form.image.data:
            # TODO fix this
            path = os.path.join(app.config['UPLOAD_PATH'], form.image.data.filename) 
            form.image.data.save(path)

        db.add_stream_content(current_user.id, 
                              form.content.data, 
                              form.image.data.filename, 
                              datetime.now())

        # reload stream
        return redirect(url_for('stream', username=username))

    # GET: load stream content
    posts = db.get_stream_content(current_user.id)
    return render_template('stream.html', 
                            title='Stream', 
                            username=username, 
                            form=form, 
                            posts=posts)

# comment page for a given post and user.
@app.route('/comments/<username>/<int:p_id>', methods=['GET', 'POST'])
@login_required
def comments(username, p_id):

    form = CommentsForm()
    if form.is_submitted():
        user = db.query_db('SELECT * FROM Users WHERE username=?;', parameters=(username,), one=True)
        db.query_db('INSERT INTO Comments (p_id, u_id, comment, creation_time) VALUES(?, ?, ?, ?);', parameters=(p_id, user['id'], form.comment.data, datetime.now()))


    post = db.get_post(p_id)
    all_comments = db.get_comments(p_id)
    return render_template('comments.html', title='Comments', username=username, form=form, post=post, comments=all_comments)

# page for seeing and adding friends
@app.route('/friends/<username>', methods=['GET', 'POST'])
@login_required
def friends(username):
    form = FriendsForm()
    user = db.query_db('SELECT * FROM Users WHERE username=?;', parameters=(username,), one=True)
    if form.is_submitted():
        friend = db.query_db('SELECT * FROM Users WHERE username=?;', parameters=(form.username.data,), one=True)
        if friend is None:
            flash('User does not exist')
        else:
            db.query_db('INSERT INTO Friends (u_id, f_id) VALUES(?, ?);', parameters=(user['id'], friend['id']))
    
    all_friends = db.query_db('SELECT * FROM Friends AS f JOIN Users as u ON f.f_id=u.id WHERE f.u_id=? AND f.f_id!=? ;', parameters=(user['id'], user['id']))
    return render_template('friends.html', title='Friends', username=username, friends=all_friends, form=form)

# see and edit detailed profile information of a user
@app.route('/profile/<username>', methods=['GET', 'POST'])
@login_required
def profile(username):
    form = ProfileForm()
    if form.is_submitted():
        db.query_db('UPDATE Users SET education=?, employment=?, music=?, movie=?, nationality=?, birthday=? WHERE username=? ;', parameters=(
            form.education.data, form.employment.data, form.music.data, form.movie.data, form.nationality.data, form.birthday.data, username
        ))
        return redirect(url_for('profile', username=username))
    
    user = db.query_db('SELECT * FROM Users WHERE username=?;', parameters=(username,), one=True)
    return render_template('profile.html', title='profile', username=username, user=user, form=form)