from app import db
from app.model.user import User
from app.model.container_auth import UserContainer
import json



class Container(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    domain = db.Column(db.String(150))
    description = db.Column(db.String(100))
    delete_flag = db.Column(db.Boolean)

    def update(self, name, domain, description):
        self.name = name
        self.description = description
        self.domain = domain
        db.session.commit()


    @staticmethod
    def get(id:int):
        return Container.query.get(id)

    @staticmethod
    def get_by_name(name:str):
        return Container.query.filter(Container.name == name).first()
    
    @staticmethod
    def save_empty_entity(user_id):
        container = Container()
        db.session.add(container)
        container.users.append(User.get(user_id))
        db.session.commit()

        return container


    @staticmethod
    def save(name:str, description:str, domain:str, user_id:int):
        container = Container(
            name = name, description=description, domain=domain, delete_flag=False)
        db.session.add(container)
        container.users.append(User.get(user_id))
        db.session.commit()

        return container
    
    @staticmethod
    def delete(user_id, container_id):
        user_container = UserContainer.get(user_id, container_id)
        db.session.delete(user_container)
        db.session.delete(Container.get(container_id))
        db.session.commit()

    @staticmethod
    def get_mediums(container_name: str):
        container = Container.get_by_name(container_name)
        return container.mediums
    
    @staticmethod
    def get_events(container_name: str):
        container = Container.get_by_name(container_name)
        return container.events