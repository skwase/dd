from __future__ import annotations

import os

from flask import Flask, redirect, url_for

from . import login_manager
from .models import db, User
from .auth import auth_bp
from .tickets import tickets_bp


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)

    # Flask sessions/flash require SECRET_KEY
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or "dev-secret"

    app.config.setdefault(
        "SQLALCHEMY_DATABASE_URI",
        os.environ.get(
            "DATABASE_URL",
            "sqlite:///%s" % os.path.join(app.instance_path, "database.db"),
        ),
    )
    app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)

    if test_config:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    # user_loader объявлен в app/models.py

    app.register_blueprint(auth_bp)
    app.register_blueprint(tickets_bp)

    @app.get("/")
    def index():
        from flask_login import current_user

        if current_user.is_authenticated:
            return redirect(url_for("tickets.list_tickets"))
        return redirect(url_for("auth.login"))

    with app.app_context():
        db.create_all()

    return app

