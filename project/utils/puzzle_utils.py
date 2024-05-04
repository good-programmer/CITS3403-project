from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func, text, desc, asc
from ..blueprints.models import db, User, Puzzle, Rating, LeaderboardRecord

from project.config import Config

def add_puzzle(title, creator, content) -> Puzzle:
    '''Add a puzzle with a given title, creator and content.'''
    puzzle = Puzzle(title=title, creator=creator, content=content)
    db.session.add(puzzle)
    if not Config.TESTING:
        db.session.commit()
    return puzzle

def get_puzzle(title=None, id=None) -> Puzzle:
    '''Retrieves a puzzle given either title or id.'''
    puzzle = None
    if title:
        puzzle = Puzzle.query.filter_by(title=title).first()
    if id:
        puzzle = Puzzle.query.filter_by(id=id).first()
    return puzzle

def search_puzzles(query, rating, date, completed, play_count, sort_by, order):
    '''Retrieves puzzles given filters. In particular, returns the query that will result in the list of puzzles matching the filters.'''
    result = Puzzle.query
    result = result.join(User, Puzzle.creatorID==User.id).filter(Puzzle.title.regexp_match(query) | User.name.regexp_match(query))
    result = result.outerjoin(Rating, Puzzle.id==Rating.puzzleID).group_by(Puzzle.id).having(func.coalesce(func.avg(Rating.rating), 0).between(rating[0],rating[1]))
    result = result.filter(Puzzle.dateCreated.between(date[0], date[1]))
    result = result.filter(Puzzle.play_count.between(play_count[0], play_count[1]))
    result = result.outerjoin(LeaderboardRecord, LeaderboardRecord.puzzleID==Puzzle.id)
    if completed:
        if completed[1] is True:
             result = result.filter(LeaderboardRecord.userID==completed[0].id)
        else:
            exclude = list(result.filter(LeaderboardRecord.userID==completed[0].id).with_entities(Puzzle.id).all())
            exclude = [i[0] for i in exclude]
            result = result.filter(Puzzle.id.not_in(exclude))

    order = asc if order == 'asc' else desc
    match sort_by:
        case 'date':
            result = result.order_by(order(Puzzle.dateCreated))
        case 'play_count':
            result = result.order_by(order(Puzzle.play_count))
        case 'highscore':
            result = result.order_by(order(func.coalesce(func.max(LeaderboardRecord.score), 0)))
        case 'rating':
            result = result.order_by(order(func.coalesce(func.avg(Rating.rating), 0)))
        case 'a-z':
            result = result.order_by(order(Puzzle.title))
            
    return result