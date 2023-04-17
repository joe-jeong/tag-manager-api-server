from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from oauthlib.oauth2 import WebApplicationClient

from config import GOOGLE_CLIENT_ID
import config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
client = WebApplicationClient(GOOGLE_CLIENT_ID)

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    #User session management setup
    login_manager.init_app(app)

    # ORM
    db.init_app(app)
    migrate.init_app(app, db)
    from . import models

    from .controller import login_controller
    app.register_blueprint(login_controller.bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(ssl_context="adhoc")