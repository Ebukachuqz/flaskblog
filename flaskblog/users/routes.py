import json
from flask import Blueprint, render_template, url_for, flash, redirect, request
from flaskblog import db, bcrypt
from flaskblog.users.forms import (RegisterationForm, LoginForm, UpdateAccountForm,
                                         RequestResetPasswordForm, NewPasswordForm)
from flaskblog.users.models import User
from flaskblog.posts.models import Post
from flask_login import login_user, logout_user, current_user, login_required
from flaskblog.users.utils import send_reset_email, save_picture
from flaskblog import oauth


users = Blueprint('users', __name__)


@users.route("/user/<string:username>")
def user_page(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_page.html', posts=posts, user=user)


@users.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterationForm()

    # validate the form
    if form.validate_on_submit():
        # hash the password inputed
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        # create an instance for the user and add to the db
        username = form.username.data
        email = form.email.data
        password = hashed_password
        
        user = User(username=username, email=email, password=password)

        # add user to db
        db.session.add(user)
        db.session.commit()

        flash(f'Account Created Successfully', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@users.route("/login", methods=['GET', 'POST'])
def login():
    # check if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = LoginForm()
    # validate the form
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # check if user exists and compare the hashed passwords
        if user.password==None:
            # user.password would return None if user registered With google signUp API
            flash('Login Unsucessful. Please Check Username and Password again', 'danger')
        elif user and bcrypt.check_password_hash(user.password, password=form.password.data):
            login_user(user, remember=form.remember.data)

            # redirect to page user was trying to access or home page if none
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            # else flash error message
            flash('Login Unsucessful. Please Check Username and Password again', 'danger')
    return render_template('login.html', title='Login', form=form)


@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()

    # Update username and email if form is validated
    if form.validate_on_submit():
        # update profile picture
        if form.update_profile_pic.data:
            # save picture
            picture_file = save_picture(form.update_profile_pic.data)
            current_user.image_file = picture_file

        # update username and email and commit to db
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Account updated Succefully', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    profile_pic = url_for('static', filename='profile_px/' + current_user.image_file)
    return render_template('account.html', title='Account', profile_pic=profile_pic, form=form)


# Request new password
@users.route("/reset_password", methods=['GET', 'POST'])
def request_reset():
    # ensure user must be logged out before accessing this route\
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("A message has been sent to your mail to reset your password. Please check SPAM if you can't find the mail in INBOX.", 'info')
        return redirect(url_for('users.login'))
    return render_template('request_reset.html', title='Reset Request', form=form)


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_password(token):
    # ensure user must be logged out before accessing this route
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    # validate token
    user = User.verify_reset_token(token)
    if user is None:
        flash('Sorry, that is an invalid or expired Token.', 'warning')
        return redirect(url_for('users.request_reset'))
    form = NewPasswordForm()
    # if form validates, update password in db
    if form.validate_on_submit():
        user.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        db.session.commit()
        flash('Password has been successfully updated. Please Login', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_password.html', title='Reset Password', form=form)


# Sigin with google route
@users.route('/google-login')
def google_login():
    google = oauth.create_client('google')  # create the google oauth client
    redirect_uri = url_for('users.google_auth', _external=True)
    return google.authorize_redirect(redirect_uri)


@users.route('/google-auth')
def google_auth():
    google = oauth.create_client('google')  # create the google oauth client
    token = google.authorize_access_token()  # Access token from google to get user info
    resp = google.get('userinfo')  # userinfo contains params specificed in the scope
    user_json = resp.json()

    # Check that email is verified by google
    if resp.json().get("verified_email"):
        # Check if user is already registered
        user = User.query.filter_by(email=user_json["email"]).first()
        if user:
            login_user(user)
            next_page = request.args.get('next')
            # if user was trying to access a page before redirect them there else to Home page
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            # register user and log them in
            username = user_json["name"]
            email = user_json["email"]
            
            user = User(username=username, email=email)

            # add user to db
            db.session.add(user)
            db.session.commit()

            flash(f'Account Created Successfully', 'success')
            # query db and login user
            user = User.query.filter_by(email=user_json["email"]).first()
            login_user(user)
            return redirect(url_for('main.home'))
    else:
        # if not verified by Google redirect user to Login page
        flash("Sorry that email is not verified By Google.")
        return redirect(url_for('login'))
    #return json.dumps(user)


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))