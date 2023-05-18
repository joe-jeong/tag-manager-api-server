from app import db
from sqlalchemy import UniqueConstraint
from app.model.container import Container
from sqlalchemy.exc import IntegrityError


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    func_code = db.Column(db.String(500))
    url_reg = db.Column(db.String(150))
    container_id = db.Column(db.Integer, db.ForeignKey("container.id"))
    container = db.relationship('Container', backref='events')

    __table_args__ = (
        UniqueConstraint('name', 'container_id', name='uix_name_container'),
    )

    @staticmethod
    def get(id):
        return Event.query.get(id)
    
    @staticmethod
    def get_by_container_and_name(container_domain, event_name):
        container = Container.get_by_domain(container_domain)
        return Event.query.filter(Event.container_id==container.id, Event.name == event_name).first()

    @staticmethod
    def save(container_domain:str, name:str, func_code:str, url_reg:str):

        container = Container.get_by_domain(container_domain)
        try:
            event = Event(
                name = name,
                func_code = func_code,
                url_reg = url_reg,
                container_id = container.id
            )
            db.session.add(event)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return None

        return event
    
    @staticmethod
    def delete(name:str):
        db.session.delete(Event.get_by_container_and_name(name))
        db.session.commit()

    @staticmethod
    def delete_by_name(container_name:str, event_name:str):
        db.session.delete(Event.get_by_container_and_name(container_name, event_name))
        db.session.commit()

    def update(self, name:str, func_code:str, url_reg:str):
        self.name = name
        self.func_code = func_code
        self.url_reg = url_reg
        db.session.commit()