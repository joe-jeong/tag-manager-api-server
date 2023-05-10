from app import db
from app.model.event import Event
from app.model.medium import Medium

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    script = db.Column(db.String(500))
    param = db.Column(db.JSON)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"))
    event = db.relationship('Event', backref='tags')
    medium_id = db.Column(db.Integer, db.ForeignKey("medium.id"))
    medium = db.relationship('Medium', backref='tags')

    @staticmethod
    def get_by_event_and_medium(event_id:int, medium_id:int):
        return Tag.query.filter(
            Event.id == event_id, Medium.id == medium_id
            ).all()
    
    @staticmethod
    def get_by_id(id:int):
        return Tag.query.get(id)
    

    @staticmethod
    def save(event_id:int, medium_id:int, param:dict, script:str):
        tag = Tag(
            event_id=event_id, medium_id=medium_id, param=param, script=script
        )
        db.session.add(tag)
        db.session.commit()
        
    @staticmethod
    def delete(id:int):
        db.session.delete(Tag.get_by_id(id))
        db.session.commit()

    
    def update(self, param:dict, script:str):
        self.param = param
        self.script = script
        db.session.commit()