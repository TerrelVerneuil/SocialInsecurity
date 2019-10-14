from flask import render_template, flash, redirect, url_for, request, session
from app import app, query_db, get_user, User
from app.forms import IndexForm, PostForm, FriendsForm, ProfileForm, CommentsForm
from datetime import datetime, timedelta
import os
from flask_login import login_user, login_required, logout_user, current_user
import hashlib,binascii
# this file contains all the different routes, and the logic for communicating with the database

#hashes the password to store in database
def hash_pass(password):

    random_salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    password_hash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), 
                                random_salt, 100000)
    password_hash = binascii.hexlify(password_hash)
    return (random_salt + password_hash).decode('ascii')

#verifies the password inputted by user is the same
def verify_pass(stored_password,user_input):
    random_salt = stored_password[:64]
    stored_password = stored_password[64:]

    password_hashed = hashlib.pbkdf2_hmac('sha512', 
                                 user_input.encode('utf-8'), 
                                  random_salt.encode('ascii'), 
                                  100000)
    password_hashed = binascii.hexlify(password_hashed).decode('ascii')
    return password_hashed == stored_password

# home page/login/registration
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = IndexForm()
    if form.login.is_submitted() and form.login.submit.data and form.login.validate(form):
        if(form.login.validate_on_submit()):
            user = get_user(form.login.username.data)
            if user == None:
                flash('Sorry, wrong username or password!')
            elif verify_pass(user['password'], form.login.password.data) == True:
                if form.login["remember_me"].data: 
                    u = User()
                    u.username = form.login.username.data
                    login_user(u, remember=True)
                else:
                    u = User()
                    u.username = form.login.username.data
                    login_user(u)
                    #if inactive for some time, automatically log out:
                    #session.permanent = True
                    #app.permanent_session_lifetime = timedelta(minutes=10)
                    #session.modified = True
                    #flash('You have been inactive for too long. Please log in again.')
                    return redirect(url_for('stream', username=form.login.username.data))
            else:
                flash('Sorry, wrong username or password!')
        

        if(current_user.is_authenticated):
            return redirect(url_for('stream', username=current_user.get_id()))


    #added for form, validation is true creates new user
    elif form.register.is_submitted() and form.register.submit.data and form.register.validate(form):

        if query_db('SELECT * FROM Users WHERE username="{}";'.format(form.register.username.data), one=True) != None: 
            flash("This username is taken")
        else: 
            query_db('INSERT INTO Users (username, first_name, last_name, password) VALUES("{}", "{}", "{}", "{}");'.format(form.register.username.data, form.register.first_name.data,
            form.register.last_name.data, hash_pass(form.register.password.data)))

            print(form.register.password.data)

        return redirect(url_for('index'))

    return render_template('index.html', title='Welcome', form=form)

# content stream page
@app.route('/stream/<username>', methods=['GET', 'POST'])
@login_required
def stream(username):
    if(current_user.username != username):
        return redirect(url_for('stream', username = current_user.username))
    form = PostForm()
    user = get_user(username)
    if form.is_submitted() and form.content.validate(form) and form.image.validate(form):
        if form.image.data:
            path = os.path.join(app.config['UPLOAD_PATH'], form.image.data.filename)
            form.image.data.save(path)

        query_db('INSERT INTO Posts (u_id, content, image, creation_time) VALUES({}, "{}", "{}", \'{}\');'.format(user['id'], form.content.data, form.image.data.filename, datetime.now()))
        return redirect(url_for('stream', username=username))

    posts = query_db('SELECT p.*, u.*, (SELECT COUNT(*) FROM Comments WHERE p_id=p.id) AS cc FROM Posts AS p JOIN Users AS u ON u.id=p.u_id WHERE p.u_id IN (SELECT u_id FROM Friends WHERE f_id={0}) OR p.u_id IN (SELECT f_id FROM Friends WHERE u_id={0}) OR p.u_id={0} ORDER BY p.creation_time DESC;'.format(user['id']))
    return render_template('stream.html', title='Stream', username=username, form=form, posts=posts)

# comment page for a given post and user.
@app.route('/comments/<username>/<int:p_id>', methods=['GET', 'POST'])
@login_required
def comments(username, p_id):

    ant_post = query_db('SELECT COUNT(*) FROM Posts;')
    print(ant_post)

    if(current_user.username != username):
        ant_post = query_db('SELECT COUNT(*) FROM Posts;')
        print(ant_post)
        return redirect(url_for('comments', username = current_user.username))

    if (p_id > ant_post[0][0]):
        flash("You tried to go into a comment that doesn't exsist")
        return redirect(url_for('stream', username = current_user.username))

    form = CommentsForm()
    if form.is_submitted() and form.comment.validate(form):
        user = get_user(username)
        query_db('INSERT INTO Comments (p_id, u_id, comment, creation_time) VALUES({}, {}, "{}", \'{}\');'.format(p_id, user['id'], form.comment.data, datetime.now()))

    post = query_db('SELECT * FROM Posts WHERE id={};'.format(p_id), one=True)
    all_comments = query_db('SELECT DISTINCT * FROM Comments AS c JOIN Users AS u ON c.u_id=u.id WHERE c.p_id={} ORDER BY c.creation_time DESC;'.format(p_id))
    return render_template('comments.html', title='Comments', username=username, form=form, post=post, comments=all_comments)

# page for seeing and adding friends
@app.route('/friends/<username>', methods=['GET', 'POST'])
@login_required
def friends(username):
    if(current_user.username != username):
        return redirect(url_for('friends', username = current_user.username))
    form = FriendsForm()
    user = get_user(username)
    if form.is_submitted():
        friend = get_user(form.username.data)
        if friend is None:
            flash('User does not exist')
        else:
            query_db('INSERT INTO Friends (u_id, f_id) VALUES({}, {});'.format(user['id'], friend['id']))
    
    all_friends = query_db('SELECT * FROM Friends AS f JOIN Users as u ON f.f_id=u.id WHERE f.u_id={} AND f.f_id!={} ;'.format(user['id'], user['id']))
    return render_template('friends.html', title='Friends', username=username, friends=all_friends, form=form)

# see and edit detailed profile information of a user
@app.route('/profile/<username>', methods=['GET', 'POST'])
@login_required
def profile(username):
    isNotMe = False
    if(current_user.username != username):
        isNotMe = True
    form = ProfileForm()
    if form.is_submitted():
        query_db('UPDATE Users SET education="{}", employment="{}", music="{}", movie="{}", nationality="{}", birthday=\'{}\' WHERE username="{}" ;'.format(
            form.education.data, form.employment.data, form.music.data, form.movie.data, form.nationality.data, form.birthday.data, username
        ))
        return redirect(url_for('profile', username=username))
    user = get_user(username)
    return render_template('profile.html', title='Profile', username=current_user.username, user=user, form=form, showEdit=isNotMe)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have successfully logged yourself out.')
    return redirect(url_for('index'))
