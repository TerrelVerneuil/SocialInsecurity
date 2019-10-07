from flask import Flask, render_template,flash # 1.1 
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FormField, TextAreaField, FileField
from wtforms.fields.html5 import DateField

from wtforms.validators import InputRequired, DataRequired, ValidationError, Regexp, NoneOf, length, EqualTo
from app import app, query_db
# from somemodule import SomeCSRF

# defines all forms in the application, these will be instantiated by the template,
# and the routes.py will read the values of the fields
# TODO: Add validation, maybe use wtforms.validators?? # Done
# TODO: There was some important security feature that wtforms provides, but I don't remember what; implement it

class LoginForm(FlaskForm):

    username = StringField('Username',validators=[DataRequired(''),Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,'ERROR'), 
    ])
    # def validate_LoginUsername(self,field):
    #     usern = query_db('SELECT * FROM Users WHERE username="{}";'.format(self.username.data), one=True)
    #     if usern != self.username.data:
    #         raise ValidationError('Invalid username or password!')

    password = PasswordField('Password',validators=[DataRequired(''),Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,'ERROR') 
    ])
    # def validate_LoginPassword(self,field):
    #     userp = query_db('SELECT * FROM Users WHERE password="{}";'.format(self.password.data), one=True)
    #     if userp != self.password.data:
    #         raise ValidationError('Invalid username or password!')

    remember_me = BooleanField('Remember me?') # TODO: It would be nice to have this feature implemented, probably by using cookies
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    first_name = StringField('First Name',validators=[DataRequired('Enter first name'),
     length(min=3, max=20, message='Must be between 3-20 characters' ),
     Regexp('^[A-Za-z][A-Za-z]*$', 0,'only letters allowed')], 
     render_kw={'placeholder': 'First Name'})# changed #1.1
    last_name = StringField('Last Name',validators=[DataRequired(message='Enter last name'), 
    length(min=3, max=20, message='Must be between 3-20 characters' ), 
    Regexp('^[A-Za-z][A-Za-z]*$', 0,'only letters allowed')], 
    render_kw={'placeholder': 'Last Name'})# changed #1.1
    username = StringField('Username', validators=[DataRequired(message='A username is required!'), 
    length(min=8, max=30, message='Must be between 8-30 characters' ), 
    Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,'Usernames must have only letters,numbers, dots or underscores')], 
    render_kw={'placeholder': 'username'}) # changed #1.1
    def validate_username(self,field):

        user = query_db('SELECT * FROM Users WHERE username="{}";'.format(self.username.data), one=True)
        if user:
            flash('Username {} is already taken.'.format(self.username.data))
            raise ValidationError('Username {} already taken.'.format(self.username.data))
   
    password = PasswordField('Password', validators=[DataRequired('Password is required!'), 
    length(min=10, max=30, message='Must be between 10-30 characters' ), 
    Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,'Password must have only letters,numbers, dots or underscores')], 
    render_kw={'placeholder': 'password'}) # changed #1.1
    def validate_password(self,field):

        if (field.data == self.username.data):
            flash('password cannot be same as username', field.data)
            raise ValidationError('password cannot be same as username')

    confirm_password = PasswordField('Confirm Password', 
    validators=[EqualTo ('password', message='confirm password must match')], 
    render_kw={'placeholder': 'Confirm password'}) # changed#1.1
    recaptcha = RecaptchaField() # added
    submit = SubmitField('Sign Up')


class IndexForm(FlaskForm):
    login = FormField(LoginForm)
    register = FormField(RegisterForm)

class PostForm(FlaskForm):
    content = TextAreaField('New Post', render_kw={'placeholder': 'What are you thinking about?'})
    image = FileField('Image')
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
