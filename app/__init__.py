from flask import Flask
from config import Config
from app.extensions import db, login_manager
from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
    CORS(
    app,
    origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    supports_credentials=True
)

    db.init_app(app)
    login_manager.init_app(app)

    from app.models import (
        User, Category, Location,
        Report, Response, ActivityLog
    )

    from app.routes.auth import auth
    from app.routes.pages import pages
    from app.routes.student import student
    from app.routes.admin import admin
    from app.routes.campus import campus

    app.register_blueprint(auth)
    app.register_blueprint(pages)
    app.register_blueprint(student)
    app.register_blueprint(admin)
    app.register_blueprint(campus)

    return app