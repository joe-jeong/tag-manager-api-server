from app import db
from app.model.event import Event
from app.model.medium import Medium
from app.model.container import Container

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    script = db.Column(db.String(500))
    param = db.Column(db.JSON)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"))
    event = db.relationship('Event', backref='tags')
    medium_id = db.Column(db.Integer, db.ForeignKey("medium.id"))
    medium = db.relationship('Medium', backref='tags')

    @staticmethod
    def get_by_event_and_medium(container_name:str, event_name:str, medium_name:str):
        container = Container.get_by_name(container_name)
        event = Event.query.filter(Event.container_id==container.id, Event.name==event_name).first()
        medium = Medium.query.filter(Medium.container_id==container.id, Medium.name==medium_name).first()

        return Tag.query.filter(Tag.event==event, Tag.medium==medium).first()
    
    @staticmethod
    def get_by_id(id:int):
        return Tag.query.get(id)
    
    @staticmethod
    def get_by_name(name:str):
        return Tag.query.filter(Tag.name == name).first()
    

    @staticmethod
    def save(event_id:int, medium_id:int, name:str, param:dict, script:str):
        tag = Tag(
            event_id=event_id, medium_id=medium_id, name=name, param=param, script=script
        )
        db.session.add(tag)
        db.session.commit()
        
    @staticmethod
    def delete(name:str):
        db.session.delete(Tag.get_by_name(name))
        db.session.commit()

    
    def update(self, name:str, param:dict, script:str):
        self.name = name
        self.param = param
        self.script = script
        db.session.commit()