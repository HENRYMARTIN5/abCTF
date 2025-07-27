"""
Module containing Flask extensions.
"""

import flask_login  # type: ignore[import-untyped]
from flask_sqlalchemy import SQLAlchemy
from .chall import ChallengeService
import os

chall_service = ChallengeService(os.getenv("CHALLENGE_DIR", "challs"))
login_manager = flask_login.LoginManager()
db = SQLAlchemy()
