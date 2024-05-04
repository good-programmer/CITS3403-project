from ..blueprints.models import db, User

from project.config import Config

def verify_user(name, password=None) -> User:
    '''Verify a user exists by name (and if password is specified, that the user's password matches).'''
    user = User.query.filter_by(name=name).first()
    if not user:
        return
    if password is not None: 
        if user.check_password(password):
            return user
    else:    
        return user

def add_user(name, password) -> User:
    '''Add a user with given name and password to the database.'''
    new_user = User(name=name, password=password)
    db.session.add(new_user)
    if not Config.TESTING:
        db.session.commit()
    return new_user

def get_user(name=None, id=None) -> User:
    '''Retrieves a given user from the database by either id or name.'''
    user = None
    if name:
        user = User.query.filter_by(name=name).first()
    if id:
        user = User.query.filter_by(id=id).first()
    return user