import secrets
import os
from flask import url_for, current_app
from flask_mail import Message
from flaskblog import mail
from flaskblog.users.models import User

# function to save picture
def save_picture(form_picture):
    # get random hex value for file name for the picture
    random_hex = secrets.token_hex(8)
    # get the file extention
    _, file_ext = os.path.splitext(form_picture.filename)
    pic_filename = random_hex + file_ext
    # create path from root where picture would be saved
    picture_path = os.path.join(current_app.root_path, 'static/profile_px', pic_filename)
    # save profile picture
    form_picture.save(picture_path)

    # return filename of the picture
    return pic_filename


# Send password request email function
def send_reset_email(user):
    token = User.get_reset_token(user)
    msg = Message()
    msg.subject = "Reset Password"
    msg.recipients = [user.email]
    msg.sender = 'noreply@demo.com'
    msg.body = f'''To reset your password please follow the link bellow:
{ url_for('users.reset_password', token=token, _external=True) }

Please ignore if you didnt request for this.
'''
    mail.send(msg)