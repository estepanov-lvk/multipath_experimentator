from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from datetime import datetime

from app.stand.server_model import *

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    about_me = db.Column(db.String(140))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
                        digest, size)

    def __repr__(self):
        return '<User {}>'.format(self.username)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class VM(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vm_name = db.Column(db.String(20), index=True, unique=True)
    vm_control_ip = db.Column(db.String(15), index=True, unique=True)
    server_id = db.Column(db.Integer, db.ForeignKey('server.id'))

    def __repr__(self):
        return '<VM {}>'.format(self.vm_name)

class Experiment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mode = db.Column(db.String(10), index=True)
    model = db.Column(db.String(10), index=True)
    subflow = db.Column(db.Integer, index=True)
    topo = db.Column(db.String(20), index=True)
    poles = db.Column(db.Integer, index=True)
    flows = db.Column(db.Integer, index=True)
    poles_seed = db.Column(db.Integer, index=True)
    routes_seed = db.Column(db.Integer, index=True)
    cc = db.Column(db.String(20), index=True)
    distribution = db.Column(db.String(20), index=True)
    time = db.Column(db.Integer, index=True)
    probe = db.Column(db.Integer, index=True)

    def __repr__(self):
        return '<Experiment {}>'.format(self.id)
