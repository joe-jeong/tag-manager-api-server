from app import db
from app.model.event import Event
from app.model.medium import Medium
from app.model.container import Container
from sqlalchemy import UniqueConstraint
from sqlalchemy.exc import IntegrityError


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    script = db.Column(db.String(500))
    param = db.Column(db.JSON)
    container_id = db.Column(db.Integer, db.ForeignKey("container.id"))
    container = db.relationship('Container', backref='tags')
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"))
    event = db.relationship('Event', backref='tags')
    medium_id = db.Column(db.Integer, db.ForeignKey("medium.id"))
    medium = db.relationship('Medium', backref='tags')

    __table_args__ = (
        UniqueConstraint('name', 'container_id', name='uix_name_container'),
    )

    @staticmethod
    def get_by_event_and_medium(container_domain:str, platform_name:str, event_name:str):
        medium = Medium.get_by_container_and_platform(container_domain, platform_name)
        event = Event.get_by_container_and_name(container_domain, event_name)

        return Tag.query.filter(Tag.medium==medium, Tag.event==event).first()
    
    @staticmethod
    def get_by_id(id:int):
        return Tag.query.get(id)
    
    @staticmethod
    def get_by_container_and_name(container_domain:str, name:str):
        container = Container.get_by_domain(container_domain)
        return Tag.query.filter(Tag.container == container, Tag.name == name).first()
    

    @staticmethod
    def save(container_domain:str, event_name:str, platform_name:str, name:str, param:dict, script:str):
        container = Container.get_by_domain(container_domain)
        medium = Medium.get_by_container_and_platform(container_domain, platform_name)
        event = Event.get_by_container_and_name(container_domain, event_name)

        try:
            tag = Tag(
                event_id=event.id,
                medium_id=medium.id,
                container_id=container.id,
                name=name,
                param=param,
                script=script
            )
            db.session.add(tag)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return None

        return tag
        
    @staticmethod
    def delete(name:str):
        db.session.delete(Tag.get_by_name(name))
        db.session.commit()

    
    def update(self, name:str, script:str):
        self.name = name
        self.script = script
        db.session.commit()