from flask import Flask
from config import Config
from app.extensions import db, login_manager


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    from app.models import (
        User, Category, Location,
        Report, Response, ActivityLog
    )

    from app.routes.auth import auth
    from app.routes.student import student
    from app.routes.admin import admin
    from app.routes.campus import campus

    app.register_blueprint(auth)
    app.register_blueprint(student)
    app.register_blueprint(admin)
    app.register_blueprint(campus)

    return app