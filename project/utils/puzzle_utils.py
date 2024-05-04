from sqlalchemy import func, desc, asc
from ..blueprints.models import db, User, Puzzle, Rating, LeaderboardRecord

from project.config import Config

def pack_puzzle(puzzle, detail=1):
    '''Packs a puzzle's public information into a dictionary with variable detail level'''
    data = {
        "id": puzzle.id,
        "title": puzzle.title,
        "creatorID": puzzle.creatorID,
        "creator": puzzle.creator.name,
        "play_count": puzzle.play_count,
        "average_rating": puzzle.average_rating,
        "dateCreated": str(puzzle.dateCreated),
        "highscore": puzzle.highest_score
    }
    if detail > 1:
        data["content"] = puzzle.content
        data["scores"] = [{"id": s.userID, "name": s.user.name, "score": s.score, "dateSubmitted": str(s.dateSubmitted)} for s in puzzle.scores]
        data["average_score"] = puzzle.average_score
    return data


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