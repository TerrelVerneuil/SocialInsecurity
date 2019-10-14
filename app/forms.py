from flask_wtf import FlaskForm, form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FormField, TextAreaField, FileField, validators
from wtforms.fields.html5 import DateField
from flask_wtf.file import FileAllowed

# defines all forms in the application, these will be instantiated by the template,
# and the routes.py will read the values of the fields


class LoginForm(FlaskForm):
    username = StringField('Username', render_kw={'placeholder': 'Username'})
    password = PasswordField('Password', render_kw={'placeholder': 'Password'})
    remember_me = BooleanField('Remember me') # TODO: It would be nice to have this feature implemented, probably by using cookies
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    first_name = StringField('First Name', [validators.DataRequired()], render_kw={'placeholder': 'First Name'})
    last_name = StringField('Last Name', [validators.DataRequired()], render_kw={'placeholder': 'Last Name'})
    username = StringField('Username', [validators.DataRequired()],render_kw={'placeholder':  'Username'})
    password = PasswordField('Password', [validators.EqualTo('confirm_password', message='The passwords must match'),
     validators.DataRequired(),
     validators.regexp("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z0-9!@#$&()\\-`.+,/\"]{8,}$", 
     message='The password must contain minimum eight characters, at least one uppercase letter, one lowercase letter and one number :))  ')],
      render_kw={'placeholder': 'Password'})
    confirm_password = PasswordField('Confirm Password', [validators.DataRequired()], render_kw={'placeholder': 'Confirm Password'})
    submit = SubmitField('Sign Up')

class IndexForm(FlaskForm):
    login = FormField(LoginForm)
    register = FormField(RegisterForm)

class PostForm(FlaskForm):
    content = TextAreaField('New Post', [
        validators.regexp('^[ÆØÅæøåA-Za-z0-9_-]{3,120}$'), 
        validators.data_required()
    ]
    ,
     render_kw={'placeholder': 'What are you thinking about?'})
    image = FileField('Image', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Only jpg, jpeg, png or gif files')])
    submit = SubmitField('Post')

class CommentsForm(FlaskForm):
    comment = TextAreaField('New Comment', [
        validators.regexp('^[ÆØÅæøåA-Za-z0-9_-]{3,120}$'), 
        validators.data_required()
    ]
    , render_kw={'placeholder': 'What do you have to say?'})
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
