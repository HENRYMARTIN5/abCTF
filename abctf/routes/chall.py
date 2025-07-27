from flask import Blueprint, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from sqlalchemy import func

from ..render import render_template
from ..models import Solve, Team, User, get_scoreboard
from ..extensions import chall_service, db

bp = Blueprint("challenges", __name__, url_prefix="/challenges")


@bp.route("/")
@login_required
def board():
    """Displays all challenges with their CURRENT, LIVE point values."""
    all_challenges = chall_service.get_all_challenges()

    solve_counts_query = db.session.query(
        Solve.challenge_id,
        func.count(Solve.challenge_id)
    ).group_by(Solve.challenge_id).all()

    solve_counts = dict(solve_counts_query)

    solved_challenge_ids = set()
    if current_user.team:
        solved_challenge_ids = {s.challenge_id for s in current_user.team.solves}

    challenges_by_category = {}
    for chal in all_challenges:
        num_solves = solve_counts.get(chal.id, 0)
        
        current_value = chal.value(num_solves)

        challenge_data = {
            "id": chal.id,
            "title": chal.title,
            "points": current_value,
            "solved_by_user": chal.id in solved_challenge_ids
        }

        if chal.category not in challenges_by_category:
            challenges_by_category[chal.category] = []
        challenges_by_category[chal.category].append(challenge_data)

    return render_template(
        "challenges.html",
        categories=challenges_by_category
    )

@bp.route("/<string:challenge_id>")
@login_required
def detail(challenge_id):
    """Displays the details for a single challenge with its CURRENT value."""
    challenge = chall_service.get_challenge(challenge_id)
    if not challenge:
        abort(404)

    num_solves = Solve.query.filter_by(challenge_id=challenge.id).count()

    current_value = challenge.value(num_solves)

    team_solve = None
    if current_user.team:
        team_solve = Solve.query.filter_by(
            team_id=current_user.team_id, challenge_id=challenge.id
        ).first()

    return render_template(
        "challenge.html",
        challenge=challenge,
        team_solve=team_solve,
        num_solves=num_solves,
        current_value=current_value,
    )


@bp.route("/<string:challenge_id>/submit", methods=["POST"])
@login_required
def submit(challenge_id):
    """Handles the flag submission logic."""
    challenge = chall_service.get_challenge(challenge_id)
    if not challenge:
        abort(404)

    if not current_user.team:
        flash("You must be on a team to submit flags.", "warning")
        return redirect(url_for("challenges.detail", challenge_id=challenge.id))

    if Solve.query.filter_by(
        team_id=current_user.team_id, challenge_id=challenge.id
    ).first():
        flash("Your team has already solved this challenge.", "info")
        return redirect(url_for("challenges.detail", challenge_id=challenge.id))

    submitted_flag = request.form.get("flag", "").strip()
    if not submitted_flag:
        flash("You must provide a flag.", "warning")
        return redirect(url_for("challenges.detail", challenge_id=challenge.id))

    if challenge.solve(submitted_flag):
        num_prior_solves = Solve.query.filter_by(challenge_id=challenge.id).count()
        points = challenge.value(num_prior_solves)

        new_solve = Solve(
            challenge_id=challenge.id,
            user_id=current_user.id,
            team_id=current_user.team_id,
            points_awarded=points,
        )
        db.session.add(new_solve)
        db.session.commit()

        flash(f"Correct! Your team earned {points} points.", "success")
    else:
        flash("Incorrect flag. Try again!", "danger")

    return redirect(url_for("challenges.detail", challenge_id=challenge.id))
