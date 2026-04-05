from flask_login import UserMixin
from werkzeug.security import generate_password_hash

from app import db


class UserProfile(UserMixin, db.Model):
    __tablename__ = 'user_profiles'

    id         = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name  = db.Column(db.String(80), nullable=False)
    username   = db.Column(db.String(80), unique=True, nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    password   = db.Column(db.String(255), nullable=False)

    def __init__(self, first_name, last_name, username, email, password):
        self.first_name = first_name
        self.last_name  = last_name
        self.username   = username
        self.email      = email.lower()
        self.password   = generate_password_hash(password)  # hashes password

class Property(db.Model):
    __tablename__ = 'properties'

    id              = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title           = db.Column(db.String(255), nullable=False)
    description     = db.Column(db.Text, nullable=False)
    no_of_rooms     = db.Column(db.Integer, nullable=False)
    no_of_bathrooms = db.Column(db.Integer, nullable=False)
    price           = db.Column(db.String(100), nullable=False)
    property_type   = db.Column(db.String(50), nullable=False)
    location        = db.Column(db.String(255), nullable=False)
    photo           = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<Property {self.title}>'
