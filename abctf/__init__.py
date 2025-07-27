"""
abCTF - A dead-simple, extensible CTF platform.
"""

from dotenv import load_dotenv
from sqlalchemy import inspect

load_dotenv()

import os

from flask import Flask

from .extensions import db, login_manager, chall_service
from .routes import all_bp
from .models import User


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URI"]
    app.secret_key = os.environ["SECRET_KEY"]

    db.init_app(app)  # type: ignore[no-untyped-call]
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    for bp in all_bp:
        app.register_blueprint(bp)

    with app.app_context():
        inspector = inspect(db.engine)
        if not inspector.has_table(User.__tablename__):
            print("Database tables not found, creating them...")
            db.create_all()
            print("Tables created.")

            admin_user = os.environ.get("ADMIN_USER").strip()
            admin_pass = os.environ.get("ADMIN_PASS").strip()

            if admin_user and admin_pass:
                if not User.query.filter_by(username=admin_user).first():
                    admin = User(username=admin_user, is_admin=True)
                    admin.set_password(admin_pass)
                    db.session.add(admin)
                    db.session.commit()
                    print(f"Default admin user '{admin_user}':'{admin_pass}' created.")
                else:
                    print(f"Admin user '{admin_user}' already exists.")
            else:
                print("ADMIN_USER or ADMIN_PASS not set, skipping admin creation.")

    chall_service.load_challenges()

    return app
