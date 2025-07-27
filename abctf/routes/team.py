from flask import Blueprint, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..models import db, User, Team
from ..render import render_template

bp = Blueprint("team", __name__, url_prefix="/team")


@bp.route("/")
@login_required
def my_team():
    """
    Redirects the user to their team's page if they are on one.
    If the user is not on a team, it redirects them to the list of all teams.
    """
    if current_user.team_id:
        return redirect(url_for("team.view_team", team_id=current_user.team.id))
    else:
        flash("You are not currently on a team.")
        return redirect(url_for("team.list_teams"))


@bp.route("/create", methods=["GET", "POST"])
@login_required
def create_team():
    """
    Allows a logged-in user who is not already on a team to create one.
    The creator automatically becomes the first member and the captain.
    """
    if current_user.team:
        flash("You are already on a team and cannot create a new one.")
        return redirect(url_for("team.view_team", team_id=current_user.team.id))

    if request.method == "POST":
        team_name = request.form.get("team_name")
        if not team_name:
            flash("Team name cannot be empty.")
            return redirect(url_for("team.create_team"))

        existing_team = Team.query.filter_by(name=team_name).first()
        if existing_team:
            flash("A team with this name already exists.")
            return redirect(url_for("team.create_team"))

        new_team = Team(name=team_name)

        db.session.add(new_team)
        db.session.flush()

        current_user.team_id = new_team.id
        new_team.captain_id = current_user.id

        db.session.commit()
        flash(f"Team '{new_team.name}' created successfully!")
        return redirect(url_for("team.view_team", team_id=new_team.id))

    return render_template("create_team.html")


@bp.route("/<int:team_id>")
@login_required
def view_team(team_id):
    """Displays the team's details."""
    team = Team.query.get_or_404(team_id)
    available_users = User.query.filter_by(team_id=None).all()
    invite_url = url_for('team.join_by_invite', invite_code=team.invite_code, _external=True)

    return render_template(
        "team_details.html", team=team, available_users=available_users, invite_url=invite_url
    )


@bp.route("/list")
@login_required
def list_teams():
    """Displays a list of all existing teams."""
    all_teams = Team.query.all()
    return render_template("list_teams.html", teams=all_teams)


@bp.route("/join/<string:invite_code>", methods=["GET", "POST"])
@login_required
def join_by_invite(invite_code):
    """Join a team using an invite code."""
    team = Team.query.filter_by(invite_code=invite_code).first_or_404()

    if request.method == "POST":
        if current_user.team:
            flash("You must leave your current team before joining a new one.")
            return redirect(url_for("team.view_team", team_id=current_user.team.id))

        current_user.team_id = team.id
        db.session.commit()

        flash(f"Welcome! You have successfully joined team '{team.name}'.")
        return redirect(url_for("team.view_team", team_id=team.id))

    return render_template("join_team.html", team=team)


@bp.route("/<int:team_id>/remove/<int:user_id>", methods=["POST"])
@login_required
def remove_member(team_id, user_id):
    """Removes a user from a team. Only the captain can perform this."""
    team = Team.query.get_or_404(team_id)
    if current_user.id != team.captain_id:
        flash("Only the team captain can remove members.")
        return redirect(url_for("team.view_team", team_id=team.id))

    if current_user.id == user_id:
        flash("The captain cannot remove themselves from the team.")
        return redirect(url_for("team.view_team", team_id=team.id))

    user_to_remove = User.query.get_or_404(user_id)
    if user_to_remove.team_id != team.id:
        flash("This user is not on your team.")
        return redirect(url_for("team.view_team", team_id=team.id))

    user_to_remove.team_id = None
    db.session.commit()
    flash(f"{user_to_remove.username} has been removed from the team.")
    return redirect(url_for("team.view_team", team_id=team.id))


@bp.route("/<int:team_id>/set_captain/<int:user_id>", methods=["POST"])
@login_required
def set_captain(team_id, user_id):
    """Sets a new captain for the team. Only the current captain can do this."""
    team = Team.query.get_or_404(team_id)
    if current_user.id != team.captain_id:
        flash("Only the team captain can assign a new captain.")
        return redirect(url_for("team.view_team", team_id=team.id))

    new_captain = User.query.get_or_404(user_id)
    if new_captain.team_id != team.id:
        flash("The new captain must be a member of the team.")
        return redirect(url_for("team.view_team", team_id=team.id))

    team.captain_id = new_captain.id
    db.session.commit()
    flash(f"{new_captain.username} is now the captain.")
    return redirect(url_for("team.view_team", team_id=team.id))
