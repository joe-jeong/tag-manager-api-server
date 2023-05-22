from app import db
from app.model.user import User
from app.model.container_auth import UserContainer
from sqlalchemy import UniqueConstraint
from sqlalchemy.exc import IntegrityError
import json



class Container(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    domain = db.Column(db.String(150))
    description = db.Column(db.String(100))
    delete_flag = db.Column(db.Boolean)

    __table_args__ = (
        UniqueConstraint('domain', name='uix_domain'),
    )


    @staticmethod
    def get(id:int):
        return Container.query.get(id)

    @staticmethod
    def get_by_domain(domain:str):
        return Container.query.filter(Container.domain == domain).first()

    @staticmethod
    def save(description:str, domain:str, user_code:str):
        try:
            container = Container(
                description=description, domain=domain, delete_flag=False)
            db.session.add(container)
            container.users.append(User.get(user_code))
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return None

        return container
    
    @staticmethod
    def delete(user_id, container_domain):
        user_container = UserContainer.get(user_id, container_domain)
        db.session.delete(user_container)
        db.session.delete(Container.get(container_domain))
        db.session.commit()

    @staticmethod
    def get_mediums(container_domain: str):
        container = Container.get_by_domain(container_domain)
        return container.mediums
    
    @staticmethod
    def get_events(container_domain: str):
        container = Container.get_by_domain(container_domain)
        return container.events
    

    def update(self, domain, description):
      self.description = description
      self.domain = domain
      db.session.commit()