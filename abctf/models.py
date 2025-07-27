from __future__ import annotations
from datetime import datetime
from typing import List, Optional
import uuid

from flask_login import UserMixin
from sqlalchemy import ForeignKey, Integer, String, Boolean, desc, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash

from .extensions import db, login_manager


class Solve(db.Model):
    __tablename__ = "solve"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    challenge_id: Mapped[str] = mapped_column(String(128), nullable=False)
    points_awarded: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    team_id: Mapped[int] = mapped_column(ForeignKey("team.id"), nullable=False)

    user: Mapped["User"] = relationship(back_populates="solves", foreign_keys=[user_id])
    team: Mapped["Team"] = relationship(back_populates="solves", foreign_keys=[team_id])


class Team(db.Model):
    __tablename__ = "team"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    captain_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("user.id"), nullable=True
    )
    captain: Mapped[Optional["User"]] = relationship(
        "User", back_populates="captain_of", foreign_keys=[captain_id]
    )

    users: Mapped[List["User"]] = relationship(
        "User", back_populates="team", foreign_keys="User.team_id"
    )

    solves: Mapped[List["Solve"]] = relationship(
        "Solve", back_populates="team", foreign_keys="Solve.team_id"
    )

    invite_code: Mapped[str] = mapped_column(
        String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4())
    )

    @property
    def score(self) -> int:
        """Total current score of the team across all solves."""
        total = (
            db.session.query(func.sum(Solve.points_awarded))
            .filter_by(team_id=self.id)
            .scalar()
        )
        return total or 0

    def __repr__(self) -> str:
        return f"<Team {self.name}>"


class User(UserMixin, db.Model):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[Optional[str]] = mapped_column(String(128))
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    team_id: Mapped[Optional[int]] = mapped_column(ForeignKey("team.id"), nullable=True)
    team: Mapped[Optional["Team"]] = relationship(
        "Team", back_populates="users", foreign_keys=[team_id]
    )

    captain_of: Mapped[Optional["Team"]] = relationship(
        "Team", back_populates="captain", foreign_keys="Team.captain_id", uselist=False
    )

    solves: Mapped[List["Solve"]] = relationship(
        "Solve", back_populates="user", foreign_keys="Solve.user_id"
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)

    def is_captain_of(self, team: Team) -> bool:
        return team.captain_id == self.id

    def __repr__(self) -> str:
        return f"<User {self.username}>"


@login_manager.user_loader
def load_user(user_id: str) -> Optional[User]:
    return User.query.get(int(user_id))


def get_scoreboard():
    """
    Generates the scoreboard data.
    Returns a list of dicts: 
    [{'rank': 1, 'team_name': 'Team A', 'score': 500, 'last_solve_at': datetime, 'last_solve_by': 'user1'}, ...]
    """
    latest_solve_subquery = db.session.query(
        Solve.team_id,
        func.max(Solve.created_at).label('max_created_at')
    ).group_by(Solve.team_id).subquery()

    scoreboard_query = db.session.query(
        Team.name.label('team_name'),
        func.sum(Solve.points_awarded).label('score'),
        User.username.label('last_solve_by'),
        latest_solve_subquery.c.max_created_at.label('last_solve_at')
    ).join(Solve, Team.id == Solve.team_id)\
     .join(latest_solve_subquery, Team.id == latest_solve_subquery.c.team_id)\
     .join(User, Solve.user_id == User.id)\
     .filter(Solve.created_at == latest_solve_subquery.c.max_created_at)\
     .group_by(Team.name, User.username, latest_solve_subquery.c.max_created_at)\
     .order_by(desc('score'), 'last_solve_at')

    all_teams_query = db.session.query(Team.name).all()
    solved_teams_data = scoreboard_query.all()
    
    scoreboard_data = [row._asdict() for row in solved_teams_data]
    
    solved_team_names = {row['team_name'] for row in scoreboard_data}
    
    for team_name_tuple in all_teams_query:
        team_name = team_name_tuple[0]
        if team_name not in solved_team_names:
            scoreboard_data.append({
                'team_name': team_name,
                'score': 0,
                'last_solve_at': None,
                'last_solve_by': None
            })

    scoreboard_data.sort(
        key=lambda x: (x["score"], (x["last_solve_at"] or datetime.min)), reverse=True
    )

    for i, row in enumerate(scoreboard_data):
        row['rank'] = i + 1
        
    return scoreboard_data