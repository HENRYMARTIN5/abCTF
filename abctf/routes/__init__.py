from .main import bp as main_bp

from typing import List

from flask import Blueprint

all_bp: List[Blueprint] = [
    main_bp
]
