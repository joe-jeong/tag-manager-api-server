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
api = Api(
    version='0.1',
    title="Tag Container Manager API Server",
    description="사이트 별 전환 스크립트를 관리하기 위한 api 서버",
    terms_url="/",
    contact="joe.jeong@cheilpengtai.com"
    )

def register_router(app: Flask):
    from app.apis import container, auth, script

    app.register_blueprint(auth.bp)
    api.add_namespace(container.ns)
    api.add_namespace(script.ns)


# TODO: 환경에 따른 config값 변경

def create_app():
    app = Flask(__name__)
    app.config.from_object(DevConfig)

    # CORS
    CORS(app, resources={r"/*": {"origins": "*"}})

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

    # restx
    api.init_app(app)

    register_router(app)

    return app

