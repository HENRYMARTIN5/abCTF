from ..models import User
from ..render import render_template

from flask import Blueprint
from flask import request, redirect, url_for, flash, render_template_string
from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user,
)

bp = Blueprint("auth", __name__)

@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()
        if user is None or not user.check_password(request.form["password"]):
            flash("Invalid username or password")
            return redirect(url_for("auth.login"))
        login_user(user)
        return redirect(url_for("main.index"))
    return render_template("login.html")