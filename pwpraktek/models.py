from app import db

class user(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    role = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
