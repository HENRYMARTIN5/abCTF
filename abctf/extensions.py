"""
Module containing Flask extensions.
"""

import flask_login  # type: ignore[import-untyped]
from flask_sqlalchemy import SQLAlchemy

login_manager = flask_login.LoginManager()
db = SQLAlchemy()
