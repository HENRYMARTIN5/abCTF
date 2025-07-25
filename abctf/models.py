from flask_login import UserMixin
from .extensions import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    users = db.relationship("User", back_populates="team")

    def __repr__(self):
        return f"<Team {self.name}>"

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    team_id = db.Column(db.Integer, db.ForeignKey("team.id"), nullable=True) # nullable - user *doesn't* have to be on a team
    team = db.relationship("Team", back_populates="users")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))