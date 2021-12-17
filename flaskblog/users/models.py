from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flaskblog import db, login_manager
from flask import current_app
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=True)
    posts = db.relationship('Post', backref='author', lazy=True)

    # Method to get token
    def get_reset_token(self, expiry_sec=1800):
        # initialize Serializer
        s = Serializer(current_app.config['SECRET_KEY'], expiry_sec)
        # get token for user
        token = s.dumps({'user_id': self.id}).decode('utf-8')
        return token

    # Method to verify token
    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        # check if token has a user_id payload in it
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"