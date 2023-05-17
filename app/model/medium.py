from app import db
from sqlalchemy import func, UniqueConstraint
from app.model.container import Container
from sqlalchemy.exc import IntegrityError

import json

class PlatformList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    form = db.Column(db.String(500))

    @staticmethod
    def get_all():
        return PlatformList.query.all()
    
    @staticmethod
    def get_by_name(name:str):
        return PlatformList.query.filter(PlatformList.name == name).first()
    
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

    __table_args__ = (
        UniqueConstraint('container_id', 'platform_id', name='uix_container_platform'),
    )

    @staticmethod
    def save(container_domain:str, platform_name:str, tracking_list:dict):
        container = Container.get_by_domain(container_domain)
        platform = PlatformList.get_by_name(platform_name)
        try:
            medium = Medium(
                container_id=container.id,
                platform_id=platform.id,
                tracking_list=func.json_array(*tracking_list),
                is_using = True
            )
            db.session.add(medium)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return None

        return medium
    

    @staticmethod
    def get(id:int):
        return Medium.query.get(id)
    

    @staticmethod
    def get_by_container_and_platform(container_domain:str, platform_name:str):
        container = Container.get_by_domain(container_domain)
        platform = PlatformList.get_by_name(platform_name)

        return Medium.query.filter(Medium.container_id == container.id,
                                   Medium.platform_id == platform.id).first()
    
    @staticmethod
    def delete_by_container_and_platform(container_domain:str, platform_name:str):
        medium = Medium.get_by_container_and_platform(container_domain, platform_name)
        db.session.delete(medium)
        db.session.commit()

    
    def update_tracking_list(self, tracking_list:dict):
        self.tracking_list = tracking_list
        db.session.commit()