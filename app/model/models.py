from app import db
from flask_login import UserMixin
from sqlalchemy import Enum


class OauthService(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50))

    __table_args__ = (db.UniqueConstraint('name'),)

    @staticmethod
    def get_by_name(name:str):
        return OauthService.query.filter(OauthService.name == name).first()

# association table
class UserContainer(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    container_id = db.Column(db.Integer, db.ForeignKey('container.id'), primary_key=True)

    @staticmethod
    def get(user_id, container_id):
        return UserContainer.query.filter(
            UserContainer.user_id == user_id, UserContainer.container_id == container_id).first()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    oauth_id = db.Column(db.Integer, db.ForeignKey('oauth_service.id'))
    oauth_service = db.relationship('OauthService', backref='users')
    asset_id = db.Column(db.String(100), nullable=False)
    containers = db.relationship(
        'Container', secondary = UserContainer.__table__, backref=db.backref('users', lazy=True))
    
    __table_args__ = (db.UniqueConstraint('oauth_id', 'asset_id'),)

    @staticmethod
    def get(id:int):
        return User.query.get(id)

    @staticmethod
    def get_by_oauth_asset_id(oauth_id:int, asset_id:str):
        return User.query.filter(OauthService.id == oauth_id, User.asset_id == asset_id).first()
    
    @staticmethod
    def save(oauth_id, asset_id):
        user = User(oauth_id=oauth_id, asset_id=asset_id)
        db.session.add(user)
        db.session.commit()
    
    @staticmethod
    def get_containers(user_id: int):
        user = User.get(user_id)
        return user.containers


class Container(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(100))
    file_name = db.Column(db.String(100))
    file_path = db.Column(db.String(200))

    def update(self, name, description, file_name, file_path):
        self.name = name
        self.description = description
        self.file_name = file_name
        self.file_path = file_path
        db.session.commit()


    @staticmethod
    def get(id:int):
        return Container.query.get(id)
    
    @staticmethod
    def save_empty_entity(user_id):
        container = Container()
        db.session.add(container)
        container.users.append(User.get(user_id))
        db.session.commit()

        return container


    @staticmethod
    def save(name, description, file_name, file_path, user_id):
        container = Container(
            name = name, description=description, file_name=file_name, file_path=file_path)
        db.session.add(container)
        container.users.append(User.get(user_id))
        db.session.commit()

        return container

    @staticmethod
    def update_info(id, name, desc):
        container = Container.get(id)
        container.name = name
        container.description = desc
        db.session.commit()
    
    @staticmethod
    def delete(user_id, container_id):
        user_container = UserContainer.get(user_id, container_id)
        db.session.delete(user_container)
        db.session.delete(Container.get(container_id))
        db.session.commit()


class Script(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100))
    file_name = db.Column(db.String(100), nullable=False)
    file_path = db.Column(db.String(200), nullable=False)
    container_id = db.Column(db.Integer, db.ForeignKey('container.id'))
    container = db.relationship('Container', backref='scripts')

    @staticmethod
    def get(id:int):
        return Script.query.get(id)

    @staticmethod
    def save(name, description, file_name, file_path, container_id):
        script = Script(
            name = name, description=description, file_name=file_name, file_path=file_path, container_id=container_id)
        db.session.add(script)
        db.session.commit()

    @staticmethod
    def update(id, name, desc):
        script = Script.get(id)
        script.name = name
        script.description = desc
        db.session.commit()
    
    @staticmethod
    def delete(script_id):
        user_container = Script.get(script_id)
        db.session.delete(user_container)
        db.session.commit()
        