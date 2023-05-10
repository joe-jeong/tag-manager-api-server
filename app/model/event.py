from app import db

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    func_code = db.Column(db.String(500))
    url_reg = db.Column(db.String(150))
    container_id = db.Column(db.Integer, db.ForeignKey("container.id"))
    container = db.relationship('Container', backref='events')

    @staticmethod
    def get(id):
        return Event.query.get(id)

    @staticmethod
    def save(container_id:int, name:str, func_code:str, url_reg:str):
        event = Event(
            container_id=container_id, name=name, func_code=func_code, url_reg=url_reg
        )
        db.session.add(event)
        db.session.commit()
    
    @staticmethod
    def delete(id:int):
        db.session.delete(Event.get(id))
        db.session.commit()

    def update(self, name:str, event_func:str, url_reg:str):
        self.name = name
        self.event_func = event_func
        self.url_reg = url_reg
        db.session.commit()