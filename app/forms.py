from flask import Flask, render_template, flash # 1.1 
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FormField, TextAreaField
from flask_wtf.file import FileField, FileAllowed
from wtforms.fields.html5 import DateField
from wtforms.validators import InputRequired, DataRequired, ValidationError, Regexp, NoneOf, length, EqualTo
from app import app
from app.db import get_user
from config import Config

class LoginForm(FlaskForm):

    username = StringField('Username')
        # validators=[DataRequired(''),
        #     Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,'ERROR')])

    password = PasswordField('Password',
        validators=[DataRequired(''),
            Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,'ERROR')])

    # login_recaptcha = RecaptchaField()
    remember_me = BooleanField('Remember me?')

    recaptcha = RecaptchaField()  
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    first_name = StringField('First Name',
        validators=[DataRequired('Enter first name'),
            length(min=2, max=20, message='Must be between 2-20 characters' ),
            Regexp('^[A-Za-z][A-Za-z]*$', 0,'only letters allowed')], 
        render_kw={'placeholder': 'First Name'})#  

    last_name = StringField('Last Name',
        validators=[DataRequired(message='Enter last name'), 
            length(min=2, max=20, message='Must be between 2-20 characters' ), 
            Regexp('^[A-Za-z][A-Za-z]*$', 0,'only letters allowed')], 
        render_kw={'placeholder': 'Last Name'})#  
    
    username = StringField('Username', 
        validators=[DataRequired(message='A username is required!'), 
            length(min=6, max=30, message='Must be between 6-30 characters' ), 
            Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,'Usernames must have only letters,numbers, dots or underscores')], 
        render_kw={'placeholder': 'username'}) #  
   
    password = PasswordField('Password', 
        validators=[DataRequired('Password is required!'), 
            length(min=8, max=30, message='Must be between 8-30 characters' ), 
            Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,'Password must have only letters,numbers, dots or underscores')], 
        render_kw={'placeholder': 'password'}) #  

    confirm_password = PasswordField('Confirm Password', 
        validators=[EqualTo ('password', message='confirm password must match')], 
        render_kw={'placeholder': 'Confirm password'}) #  
    
    submit = SubmitField('Sign Up')

    def validate_username(self, field):
        user = get_user(self.username.data)
        if user:
            flash('Username {} is already taken.'.format(self.username.data))
            raise ValidationError('Username {} already taken.'.format(self.username.data))

    def validate_password(self, field):
        if (field.data == self.username.data):
            flash('password cannot be same as username', field.data)
            raise ValidationError('password cannot be same as username')

class IndexForm(FlaskForm):
    login = FormField(LoginForm)
    register = FormField(RegisterForm)

class PostForm(FlaskForm):
    content = TextAreaField('New Post', render_kw={'placeholder': 'What are you thinking about?'})
    image = FileField('Image', validators=[
        FileAllowed(Config.ALLOWED_EXTENSIONS, 'Images only!')
    ])
    submit = SubmitField('Post')

class CommentsForm(FlaskForm):
    comment = TextAreaField('New Comment', render_kw={'placeholder': 'What do you have to say?'})
    submit = SubmitField('Comment')

class FriendsForm(FlaskForm):
    username = StringField('Friend\'s username', render_kw={'placeholder': 'Username'})
    submit = SubmitField('Add Friend')

class ProfileForm(FlaskForm):
    education = StringField('Education', render_kw={'placeholder': 'Highest education'})
    employment = StringField('Employment', render_kw={'placeholder': 'Current employment'})
    music = StringField('Favorite song', render_kw={'placeholder': 'Favorite song'})
    movie = StringField('Favorite movie', render_kw={'placeholder': 'Favorite movie'})
    nationality = StringField('Nationality', render_kw={'placeholder': 'Your nationality'})
    birthday = DateField('Birthday')
    submit = SubmitField('Update Profile')
