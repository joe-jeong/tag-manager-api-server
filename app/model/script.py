from app import db
from app.model.event import Event
from app.model.medium import Medium
from app.model.container import Container
from sqlalchemy import UniqueConstraint, desc
from sqlalchemy.exc import IntegrityError
from datetime import datetime

class Script(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100))
    s3_path = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.now)
    container_id = db.Column(db.Integer, db.ForeignKey("container.id"))
    container = db.relationship('Container', backref='scripts')

    @staticmethod
    def save(filename:str, s3_path:str, container:Container):
        script = Script(filename=filename, s3_path=s3_path, container=container)
        db.session.add(script)
        db.session.commit()
    
    @staticmethod
    def get_recent_script(container:Container):
        return Script.query.filter(Script.container==container).order_by(desc(Script.created_at)).first()
