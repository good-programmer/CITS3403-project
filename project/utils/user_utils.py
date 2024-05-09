from ..blueprints.models import db, User
from . import puzzle_utils

from project import config

def pack_user(user:User) -> dict:
    '''Packs a user's public information into a dictionary'''
    return {
            "id": user.id,
            "username": user.name,
            "followers": [{"id": u.followerID, "name": u.follower.name} for u in user.followers],
            "following": [{"id": u.userID, "name": u.user.name} for u in user.following],
            "scores": [{"id": s.puzzleID, "title": s.puzzle.title, "creator": s.puzzle.creator.name, "creatorID": s.puzzle.creatorID, "play_count": s.puzzle.play_count, "score": s.score, "dateSubmitted": str(s.dateSubmitted)} for s in user.scores],
            "ratings": [{"id": r.puzzleID, "title": r.puzzle.title, "creator": r.puzzle.creator.name, "creatorID": r.puzzle.creatorID, "play_count": r.puzzle.play_count, "rating": r.rating, "dateRated": str(r.dateRated)} for r in user.ratings],
            "puzzles": [puzzle_utils.pack_puzzle(p) for p in user.puzzles],
            "highscore": max((s.score for s in user.scores), default=None)
        }

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
    if not getattr(config.current_config, 'COMMITS_DISABLED', False):
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