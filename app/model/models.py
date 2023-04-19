from app import db
from flask_login import UserMixin


# association table
user_container = db.Table('user_container',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('container_id', db.Integer, db.ForeignKey('container.id'), primary_key=True)
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(100), nullable=False)
    nickname = db.Column(db.String(100), nullable=False)
    containers = db.relationship(
        'Container', secondary = user_container, backref=db.backref('users', lazy=True))

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
    
    @staticmethod
    def get_containers(user_id: int):
        user = User.get(user_id)
        return user.containers


class Container(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100))
    file_name = db.Column(db.String(100), nullable=False)
    file_path = db.Column(db.String(200), nullable=False)

    @staticmethod
    def get(id:int):
        return Container.query.get(id)

    @staticmethod
    def save(name, description, file_name, file_path, user_id):
        container = Container(
            name = name, description=description, file_name=file_name, file_path=file_path)
        db.session.add(container)
        container.users.append(User.get(user_id))
        db.session.commit()
        