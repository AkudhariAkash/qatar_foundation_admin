from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    opportunities = db.relationship(
        "Opportunity",
        backref="creator",
        lazy=True,
        cascade="all, delete-orphan",
    )

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
        }


class Opportunity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    duration = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    skills = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    future_opportunities = db.Column(db.Boolean, nullable=False, default=False)
    max_applicants = db.Column(db.Integer, nullable=False)

    admin_id = db.Column(db.Integer, db.ForeignKey("admin.id"), nullable=False, index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "duration": self.duration,
            "start_date": self.start_date,
            "description": self.description,
            "skills": self.skills,
            "category": self.category,
            "future_opportunities": self.future_opportunities,
            "max_applicants": self.max_applicants,
            "admin_id": self.admin_id,
        }
