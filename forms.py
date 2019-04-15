from flask_wtf import FlaskForm as Form

from models import User

from wtforms import StringField, PasswordField, TextAreaField, FileField, BooleanField, IntegerField
from wtforms.validators import (DataRequired, Regexp, ValidationError, Email,
                               Length, EqualTo)


def name_exists(form, field):
    if User.select().where(User.username == field.data).exists():
        raise ValidationError('User with that name already exists.')


def email_exists(form, field):
    if User.select().where(User.email == field.data).exists():
        raise ValidationError('User with that email already exists.')

class RegisterForm(Form):
    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            Regexp(
                r'^[a-zA-Z0-9_]+$',
                message=("Username should be one word, letters, "
                         "numbers, and underscores only.")
            ),
            name_exists
        ])
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(),
            email_exists
        ])
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=2),
            EqualTo('password2', message='Passwords must match')
        ])
    password2 = PasswordField(
        'Confirm Password',
        validators=[DataRequired()]
    )

class UserForm(Form):
    username = StringField(
        'Username',
        validators=[
            Regexp(
                r'^[a-zA-Z0-9_]+$',
                message=("Username should be one word, letters, "
                         "numbers, and underscores only.")
            ),
            name_exists
        ])
    email = StringField(
        'Email',
        validators=[
            Email(),
            email_exists
        ])
    password = PasswordField(
        'Password',
        validators=[
            Length(min=2)
        ])
    first_name = StringField(
        'First Name'
    )
    last_name = StringField(
        'Last Name'
    )
    skin_type = StringField(
        'Skin Type'
    )
    age = IntegerField(
        'Age'
    )
    profile_image = FileField('Profile Image')

class LoginForm(Form):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

class ReviewForm(Form):
    buy_again = BooleanField("Buy again?")
    content = TextAreaField("Enter your review here.", validators=[DataRequired()])

class VoteForm(Form):
    helpful = BooleanField('Helpful?')