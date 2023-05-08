from app import db

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    script = db.Column(db.String(500))
    param = db.Column(db.JSON)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"))
    event = db.relationship('Event', backref='tags')
    medium_id = db.Column(db.Integer, db.ForeignKey("medium.id"))
    medium = db.relationship('Medium', backref='tags')