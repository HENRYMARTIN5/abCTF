from .main import bp as main_bp
from .auth import bp as auth_bp
from .team import bp as team_bp

from typing import List

from flask import Blueprint

all_bp: List[Blueprint] = [main_bp, auth_bp, team_bp]
