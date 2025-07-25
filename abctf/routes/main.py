from ..render import render_template

from flask import Blueprint

bp = Blueprint("main", __name__)

@bp.route("/")
def index():
    return render_template("index.html")