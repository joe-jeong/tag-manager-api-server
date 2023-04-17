from container_manager import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(100), nullable=False)
    nickname = db.Column(db.String(100), nullable=False)

    def get_by_email(email:str):
        return User.query.filter(User.email == email)
    
    def create(email:str, nickname:str):
        user = User(email=email, nickname=nickname)
        db.session.add(user)
        db.session.commit()