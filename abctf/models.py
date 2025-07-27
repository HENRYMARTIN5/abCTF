from __future__ import annotations
from typing import List, Optional
import uuid

from flask_login import UserMixin
from sqlalchemy import ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash

from .extensions import db, login_manager


class Team(db.Model):
    __tablename__ = "team"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    users: Mapped[List[User]] = relationship(
        back_populates="team", foreign_keys="User.team_id"
    )

    captain_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("user.id"), nullable=True
    )
    captain: Mapped[Optional[User]] = relationship(
        back_populates="captain_of", foreign_keys=[captain_id]
    )

    invite_code: Mapped[str] = mapped_column(
        String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4())
    )

    def __repr__(self) -> str:
        return f"<Team {self.name}>"


class User(UserMixin, db.Model):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[Optional[str]] = mapped_column(String(128))
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    team_id: Mapped[Optional[int]] = mapped_column(ForeignKey("team.id"), nullable=True)

    team: Mapped[Optional[Team]] = relationship(
        back_populates="users", foreign_keys=[team_id]
    )
    captain_of: Mapped[Optional[Team]] = relationship(
        back_populates="captain", foreign_keys="[Team.captain_id]", uselist=False
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
