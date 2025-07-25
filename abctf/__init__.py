"""
abCTF - A dead-simple, extensible CTF platform.
"""

from dotenv import load_dotenv

load_dotenv()

import os

from flask import Flask

from .extensions import db, login_manager
from .routes import all_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URI"]
    app.secret_key = os.environ["SECRET_KEY"]

    db.init_app(app)  # type: ignore[no-untyped-call]
    # login_manager.init_app(app)

    for bp in all_bp:
        app.register_blueprint(bp)

    return app
