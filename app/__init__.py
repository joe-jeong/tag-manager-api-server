from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from oauthlib.oauth2 import WebApplicationClient

from app.config.flask_config import DevConfig

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
client = WebApplicationClient(DevConfig.GOOGLE_CLIENT_ID)

def register_router(app: Flask):
    from app.router import login_router

    app.register_blueprint(login_router.bp)

# TODO: 환경에 따른 config값 변경

def create_app():
    app = Flask(__name__)
    app.config.from_object(DevConfig)

    #User session management setup
    login_manager.init_app(app)

    # ORM
    db.init_app(app)
    migrate.init_app(app, db)
    from app.model import models

    register_router(app)

    return app

