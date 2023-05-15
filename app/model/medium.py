from app import db
from sqlalchemy import func
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
    name = db.Column(db.String(100))
    is_using = db.Column(db.Boolean)
    tracking_list = db.Column(db.JSON)
    container_id = db.Column(db.Integer, db.ForeignKey("container.id"))
    container = db.relationship('Container', backref='mediums')
    platform_id = db.Column(db.Integer, db.ForeignKey("platform_list.id"))
    platform = db.relationship('PlatformList', backref='mediums')

    @staticmethod
    def save(container_id:int, name:str, platform_id:int, tracking_list:dict):

        medium = Medium(
            container_id=container_id,
            name=name,
            platform_id=platform_id,
            tracking_list=func.json_array(*tracking_list)
        )
        medium.is_using = True
        db.session.add(medium)
        db.session.commit()
    
    @staticmethod
    def get(id:int):
        return Medium.query.get(id)
    
    @staticmethod
    def get_by_name(name:str):
        return Medium.query.filter(Medium.name == name).first()
    
    @staticmethod
    def delete(name:str):
        medium = Medium.get_by_name(name)
        db.session.delete(medium)
        db.session.commit()
    
    def update_name_tracking_list(self, name:str, tracking_list:dict):
        self.name = name
        self.tracking_list = tracking_list
        db.session.commit()