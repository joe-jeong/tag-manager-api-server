from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_restx import Api, Resource
from oauthlib.oauth2 import WebApplicationClient
from flask_jwt_extended import JWTManager
from flask_redis import FlaskRedis

from app.config.flask_config import LocalConfig, DevConfig


db = SQLAlchemy()
migrate = Migrate()
client = WebApplicationClient(DevConfig.GOOGLE_CLIENT_ID)
jwt = JWTManager()
redis = FlaskRedis()
authorizations = {'bearer_auth': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
        }
    }
api = Api(
    version='0.1',
    title="Tag Container Manager API Server",
    description="사이트 별 전환 스크립트를 관리하기 위한 api 서버",
    terms_url="/",
    contact="joe.jeong@cheilpengtai.com",
    authorizations=authorizations,
    security='bearer_auth'
)

def register_router(app: Flask):
    from app.apis import auth_api, container_api, medium_api, event_api, tag_api

    app.register_blueprint(auth_api.bp)
    api.add_namespace(container_api.ns)
    api.add_namespace(medium_api.ns)
    api.add_namespace(event_api.ns)
    api.add_namespace(tag_api.ns)


# TODO: 환경에 따른 config값 변경

def create_app():
    app = Flask(__name__)
    app.config.from_object(LocalConfig)

    # CORS
    CORS(app)

    # JWT
    jwt.init_app(app)

    # ORM
    db.init_app(app)
    migrate.init_app(app, db)
    from app.model import (
        container,
        container_auth,
        event,
        medium,
        oauth_service,
        tag,
        user
    )

    # Redis
    redis.init_app(app)

    # restx
    api.init_app(app)

    register_router(app)

    return app

