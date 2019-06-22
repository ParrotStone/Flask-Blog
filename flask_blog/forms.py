from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators, BooleanField, SubmitField
from wtforms.fields.html5 import EmailField


class RegisterationForm(FlaskForm):
    username = StringField('Username', validators=[
                           validators.Length(min=5, max=30)])
    email = EmailField('Email', validators=[
        validators.Email()])
    password = PasswordField('Password', validators=[validators.Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[
                                     validators.EqualTo('password')])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[
        validators.Email(), validators.DataRequired()])
    password = PasswordField('Password', validators=[
                             validators.DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log In')
