from ..render import render_template

from flask import Blueprint, current_app

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/debug")
def debug():
    if current_app.debug:
        return render_template("debug.html")
    else:
        return "Not in debug mode", 404
