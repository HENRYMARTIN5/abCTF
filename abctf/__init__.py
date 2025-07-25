"""
abCTF - A dead-simple, extensible CTF platform.
"""

from dotenv import load_dotenv

load_dotenv()

from flask import Flask
import os
from .extensions import db
from .routes import all_bp

def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URI"]

    db.init_app(app)  # type: ignore[no-untyped-call]

    for bp in all_bp:
        app.register_blueprint(bp)

    return app
