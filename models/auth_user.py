from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash

# SQLAlchemy instance will be created in app.py
# This model assumes a table 'users' already exists.

db = SQLAlchemy()

class AuthUser(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
