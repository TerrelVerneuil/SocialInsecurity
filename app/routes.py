from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from app import app, login_manager
import app.db as db
from app.auth import User, hash_password, check_password
from app.forms import IndexForm, PostForm, FriendsForm, ProfileForm, CommentsForm
from werkzeug.utils import secure_filename
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
        if user and check_password(user['password'], form.login.password.data):
            login_user(User(user), remember=form.login.remember_me)
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
    if form.validate_on_submit():
        f = form.image.data
        if f:
            filename = secure_filename(f.filename)
            path = os.path.join(app.config['UPLOAD_PATH'], filename) 
            f.save(path)
        else:
            filename = None

        db.add_stream_content(current_user.id, 
                              form.content.data, 
                              filename)

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
    # redirect if someone tries to access other peoples friends page
    if not current_user.username == username:
        return redirect(url_for('comments', username=current_user.username, p_id=p_id))

    post = db.get_post(p_id)
    if not post or not (current_user.id == post['u_id'] or db.is_user_friend(current_user.id, post['u_id'])):
        abort(404)

    form = CommentsForm()
    if form.is_submitted():
        db.add_comment(current_user.id, p_id, form.comment.data)
        post = db.get_post(p_id)

    all_comments = db.get_comments(p_id)
    return render_template('comments.html', 
                            title='Comments', 
                            username=username, 
                            form=form, 
                            post=post, 
                            comments=all_comments)


# page for seeing and adding friends
@app.route('/friends/<username>', methods=['GET', 'POST'])
@login_required
def friends(username):
    # redirect if someone tries to access other peoples friends page
    if not current_user.username == username:
        return redirect(url_for('friends', username=current_user.username))

    form = FriendsForm()
    if form.is_submitted():
        friend = db.get_user(form.username.data)
        if friend is None:
            flash('User does not exist')
        else:
            db.add_friend(current_user.id, friend['id'])
            flash('Friend request sent') # TODO add friend request?
              
    all_friends = db.get_all_friends(current_user.id)
    return render_template('friends.html', title='Friends', username=current_user.username, friends=all_friends, form=form)

# see and edit detailed profile information of a user
@app.route('/profile/<username>', methods=['GET', 'POST'])
@login_required
def profile(username):
    form = ProfileForm()
    user = db.get_user(username)
    if current_user.username == username:
        if form.is_submitted():
            db.update_profile(current_user.id, 
                form.education.data or user['education'], 
                form.employment.data or user['employment'], 
                form.music.data or user['music'], 
                form.movie.data or user['movie'], 
                form.nationality.data or user['nationality'], 
                form.birthday.data or user['birthday'])
            return redirect(url_for('profile', username=username))
    
    elif db.is_user_friend(current_user.id, user['id']):
        for field in form:
            field.render_kw = {'disabled': 'disabled'}
    else:
        return abort(404)
    
    return render_template('profile.html', title='profile', username=username, user=user, form=form)
    