from werkzeug.security import generate_password_hash, check_password_hash
from ..blueprints.models import db, User

def verify_user(name, password=None):
    user = User.query.filter_by(name=name).first()
    return user if user and (not password or check_password_hash(user.password, password)) else None

def add_user(name, password):
    new_user = User(name=name, password=generate_password_hash(password))
    db.session.add(new_user)
    db.session.commit()
    return new_user

def get_user(name=None, id=None):
    user = None
    if name:
        user = User.query.filter_by(name=name).first()
    if id:
        user = User.query.filter_by(id=id).first()
    return user