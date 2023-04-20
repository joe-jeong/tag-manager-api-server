from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
from flask_restx import Api, Resource
from oauthlib.oauth2 import WebApplicationClient
from flask_jwt_extended import JWTManager
from flask_redis import FlaskRedis

from app.config.flask_config import DevConfig

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
client = WebApplicationClient(DevConfig.GOOGLE_CLIENT_ID)
jwt = JWTManager()
redis = FlaskRedis()
api = Api()

def register_router(app: Flask):
    from app.apis import auth, conatiner, script

    app.register_blueprint(auth.bp)
    app.register_blueprint(conatiner.bp)
    app.register_blueprint(script.bp)


# TODO: 환경에 따른 config값 변경

def create_app():
    app = Flask(__name__)
    app.config.from_object(DevConfig)

    # CORS
    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    #User session management setup
    login_manager.init_app(app)

    # JWT
    jwt.init_app(app)

    # ORM
    db.init_app(app)
    migrate.init_app(app, db)
    from app.model import models

    # Redis
    redis.init_app(app)

    api.init_app(app)

    register_router(app)

    return app

