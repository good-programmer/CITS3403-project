from werkzeug.security import generate_password_hash, check_password_hash
from ..blueprints.models import db, User, Puzzle

from project.config import Config

def add_puzzle(title, creator, content):
    puzzle = Puzzle(title=title, creator=creator, content=content)
    db.session.add(puzzle)
    if not Config.TESTING:
        db.session.commit()
    return puzzle

def get_puzzle(title=None, id=None):
    puzzle = None
    if title:
        puzzle = Puzzle.query.filter_by(title=title).first()
    if id:
        puzzle = Puzzle.query.filter_by(id=id).first()
    return puzzle