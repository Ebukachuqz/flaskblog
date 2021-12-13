from flaskblog.users.models import User
from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Regexp


# Registeration Form
class RegisterationForm(FlaskForm):
    username = StringField('Username',
                            validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                            validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), 
                            Regexp('(?=.*[a-zA-Z])(?=.*[0-9])', message="Password must contain a mix of numbers and letters"), 
                            EqualTo('confirm_password', message="Passwords must match"),
                            Length(min=8, message="Password must be at least 8 Characters")])
    confirm_password = PasswordField('Confirm Password',
                            validators=[DataRequired()])
    submit = SubmitField('Sign Up')

    # Validate username
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('The Username is already taken. Please try another one')


    # validate email
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('The Email is already taken. Please use another one')


# Login Form
class LoginForm(FlaskForm):
    email = StringField('Email',
                            validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                            validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


# Update Account form
class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                            validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                            validators=[DataRequired(), Email()])
    update_profile_pic = FileField('Update Profile Picture', 
                            validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    # Validate username
    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('The Username is already taken. Please try another one')

    # validate email
    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('The Email is already taken. Please use another one')


class RequestResetPasswordForm(FlaskForm):
    email = StringField('Email',
                            validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. Please create an account.')


class NewPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), 
                            Regexp('(?=.*[a-zA-Z])(?=.*[0-9])', message="Password must contain a mix of numbers and letters"), 
                            EqualTo('confirm_password', message="Passwords must match"),
                            Length(min=8, message="Password must be at least 8 Characters")])
    confirm_password = PasswordField('Confirm Password',
                            validators=[DataRequired()])
    submit = SubmitField('Submit')