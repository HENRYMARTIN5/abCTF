from ..models import User
from ..render import render_template
from ..extensions import db

from flask import Blueprint
from flask import request, redirect, url_for, flash
from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user,
)

bp = Blueprint("auth", __name__)

# TODO: email verification


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
    return render_template("_auth.html", action="Login")


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        existing_user = User.query.filter_by(username=username).first()
        if existing_user is not None:
            flash("Username already exists")
            return redirect(url_for("auth.register"))
        user = User(username=username)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()
        return redirect(url_for("auth.login"))
    return render_template("_auth.html", action="Register")


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))
