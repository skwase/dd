from __future__ import annotations

import os

from flask import Flask, redirect, url_for
from .models import db, User

from .auth import auth_bp
from .tickets import tickets_bp


from . import login_manager


def create_app(test_config: dict | None = None) -> Flask:

    app = Flask(__name__, instance_relative_config=True)

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

    @login_manager.user_loader
    def load_user(user_id: str):
        try:
            return User.query.get(int(user_id))
        except Exception:
            return None

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

        # Обеспечим тестовые учетные записи с корректными хэшами паролей,
        # чтобы админ/ответственный всегда могли войти.
        # В login.html ожидаются креды: admin / admin123, responsible / resp123
        from werkzeug.security import generate_password_hash

        defaults = [
            ("admin", "admin@system.com", "admin123", "admin", "Системный администратор"),
            ("responsible", "responsible@system.com", "resp123", "responsible", "Ответственный"),
        ]


        for username, email, password, role, full_name in defaults:
            user = User.query.filter_by(username=username).first()
            if user is None:
                user = User(
                    username=username,
                    email=email,
                    password_hash=generate_password_hash(password),
                    role=role,
                    full_name=full_name,
                )
                db.session.add(user)
            else:
                # Обновим пароль/роль, чтобы не зависеть от того, что было в старой БД
                user.email = email
                user.role = role
                user.full_name = full_name
                user.password_hash = generate_password_hash(password)

        db.session.commit()

    return app


