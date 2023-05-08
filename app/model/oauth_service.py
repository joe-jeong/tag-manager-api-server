from app import db

class OauthService(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50))

    __table_args__ = (db.UniqueConstraint('name'),)

    @staticmethod
    def get_by_name(name:str):
        return OauthService.query.filter(OauthService.name == name).first()