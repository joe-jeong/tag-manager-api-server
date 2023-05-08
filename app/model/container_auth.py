from app import db

class Authorization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

# association table: user_container <-> authorization
class ContainerAuthorization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    authorization_id = db.Column(db.Integer, db.ForeignKey('authorization.id'))
    user_container_id = db.Column(db.Integer, db.ForeignKey('user_container.id'))


# association table: user <-> container
class UserContainer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    container_id = db.Column(db.Integer, db.ForeignKey('container.id'))
    authorizations = db.relationship(
        'Authorization', secondary = ContainerAuthorization.__table__, backref=db.backref('user_container_list', lazy=True))

    @staticmethod
    def get(user_id, container_id):
        return UserContainer.query.filter(
            UserContainer.user_id == user_id, UserContainer.container_id == container_id).first()