from app import db
from app.model.container_auth import UserContainer
from app.model.oauth_service import OauthService

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    oauth_id = db.Column(db.Integer, db.ForeignKey('oauth_service.id'))
    oauth_service = db.relationship('OauthService', backref='users')
    asset_id = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(10))
    containers = db.relationship(
        'Container', secondary = UserContainer.__table__, backref=db.backref('users', lazy=True))
    
    __table_args__ = (db.UniqueConstraint('oauth_id', 'asset_id'),)

    @staticmethod
    def get(id:int):
        return User.query.get(id)

    @staticmethod
    def get_by_oauth_asset_id(oauth, asset_id:str):
        return User.query.filter(User.oauth_service == oauth, User.asset_id == asset_id).first()
    
    @staticmethod
    def save(oauth_id, asset_id, code):
        user = User(oauth_id=oauth_id, asset_id=asset_id, code=code)
        db.session.add(user)
        db.session.commit()
    
    @staticmethod
    def get_containers(user_id: int):
        user = User.get(user_id)
        return user.containers
    
    @staticmethod
    def get_by_code(code:str):
        return User.query.filter(User.code == code).first()