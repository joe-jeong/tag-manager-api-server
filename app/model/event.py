from app import db

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    code = db.Column(db.String(500))
    url_reg = db.Column(db.String(150))
    container_id = db.Column(db.Integer, db.ForeignKey("container.id"))
    container = db.relationship('Container', backref='events')