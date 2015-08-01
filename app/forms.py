from flask_wtf import Form
from wtforms import BooleanField, TextField, PasswordField, StringField
from wtforms import validators
from wtforms.validators import DataRequired

#__all__ = [
#        'SignupForm' 
#        ]

class SignupForm(Form):
    username = StringField('User Name', [validators.length(min=4, max=25)])
    email = StringField('Email Address', [validators.length(min=6, max=35)])
    password = PasswordField('New Password', [
            validators.Required(),
            validators.EqualTo('confirm', message='Passwords must match')
        ])

    confirm = PasswordField('Repeat Password')

class LoginForm(Form):
    username = StringField('User Name', [validators.length(min=4, max=25)])
    password = PasswordField('Password', [
            validators.Required()
        ])

class PostForm(Form):
    title = StringField('Post Title', [validators.length(min=1, max=128)])  
    content = TextField('Post Content')  
