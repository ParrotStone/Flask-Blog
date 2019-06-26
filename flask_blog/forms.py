from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, validators, BooleanField, TextAreaField, ValidationError
from wtforms.fields.html5 import EmailField
from flask_login import current_user
# # This import down below is necessary in case you'd like to use the custom validation in the Login Form
# from flask_blog import app_bcrypt
from flask_blog.models import User


class RegisterationForm(FlaskForm):
    username = StringField('Username', validators=[
                           validators.Length(min=5, max=25)])
    email = EmailField('Email', validators=[
        validators.Email()])
    password = PasswordField('Password', validators=[validators.Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[
                                     validators.EqualTo('password')])

    # Custom Validations
    # Validate username availability and whitespace
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                'Username is taken. Please choose a different one.')

    # Validate email availability and whitespace
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.lower()).first()
        if user:
            raise ValidationError(
                'Email is taken. Please choose a different one. Capitalization is not considered.')

    def validate_password(self, password):
        if password.data.strip() != password.data:
            raise ValidationError(
                'Field cannot start or end with whitespaces')


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[
        validators.Email(), validators.DataRequired()])
    password = PasswordField('Password', validators=[
                             validators.DataRequired()])
    remember = BooleanField('Remember Me')

    # Custom validation for the password field of the login form
    # Although, the validation code down here works like a charm I didn't use it as it would be better for a malicious attacker to not know what 'Email' is actually in the database even if he doesn't know the password
    # def validate_password(self, password):
    # # 'self' keyword here indicate the LoginForm itself
    #     user = User.query.filter_by(email=self.email.data).first()
    #     if user:
    #         if not app_bcrypt.check_password_hash(user.password, password.data):
    #             raise ValidationError(
    #                 'Invalid password. Please enter a correct password')


class UpdateAccountForm(FlaskForm):
    username = StringField('New Username', validators=[
                           validators.Length(min=5, max=25)])
    email = EmailField('New Email', validators=[validators.Email()])
    img = FileField('New Profile Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'])])
    # img_file_upload
    brief_info = TextAreaField('About Me', validators=[
                               validators.Length(max=130)])

    # Custom validators
    def validate_username(self, username):
        if current_user.username != username.data:
            if User.query.filter_by(username=username.data).first():
                raise ValidationError(
                    'Username is already taken. Please choose a different one.')

    def validate_email(self, email):
        if current_user.email != email.data:
            if User.query.filter_by(email=email.data.lower()).first():
                raise ValidationError(
                    'Email is already taken. Please choose a different one. Capitalization is not considered.')
