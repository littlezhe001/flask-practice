from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Record_photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    photo_name = db.Column(db.String(80), unique=True, nullable=False)
    upload_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Record_video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    video_name = db.Column(db.String(80), unique=True, nullable=False)
    upload_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


