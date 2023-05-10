from app import db
import json

class PlatformList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    form = db.Column(db.String(500))

    @staticmethod
    def get_all():
        return PlatformList.query.all()
    
    @staticmethod
    def get_name(id:int):
        return PlatformList.query.get(id).name


class Medium(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    is_using = db.Column(db.Boolean)
    tracking_list = db.Column(db.JSON)
    container_id = db.Column(db.Integer, db.ForeignKey("container.id"))
    container = db.relationship('Container', backref='mediums')
    platform_id = db.Column(db.Integer, db.ForeignKey("platform_list.id"))
    platform = db.relationship('PlatformList', backref='mediums')

    @staticmethod
    def save(container_id:int, platform_id:int, tracking_list:dict):
        medium = Medium(
            container_id=container_id, platform_id=platform_id, tracking_list=tracking_list
        )
        medium.is_using = True
        db.session.add(medium)
        db.session.commit()
    
    @staticmethod
    def get(id:int):
        return Medium.query.get(id)
    
    @staticmethod
    def delete(id:int):
        medium = Medium.get(id)
        db.session.delete(medium)
        db.session.commit()
    
    def update_tracking_list(self, tracking_list:dict):
        self.tracking_list = tracking_list
        db.session.commit()