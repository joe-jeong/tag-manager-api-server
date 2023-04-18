from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(100), nullable=False)
    nickname = db.Column(db.String(100), nullable=False)

    @staticmethod
    def get(id:int):
        return User.query.get(id)

    @staticmethod
    def get_by_email(email:str):
        return User.query.filter(User.email == email).first()
    
    @staticmethod
    def save(email, username):
        user = User(email = email, nickname = username)
        db.session.add(user)
        db.session.commit()