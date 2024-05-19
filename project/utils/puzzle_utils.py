import re
from sqlalchemy import func, desc, asc
from ..blueprints.models import db, User, Puzzle, Rating, LeaderboardRecord, Follow

from project import config

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
        data["scores"] = [{"id": s.userID, "name": s.user.name, "score": s.score, "dateSubmitted": str(s.dateSubmitted)} for s in puzzle.scores]
        data["average_score"] = puzzle.average_score
        data["rating_count"] = len(puzzle.ratings)
    if detail > 2:
        data["content"] = puzzle.content
    return data


def add_puzzle(title, creator, content) -> Puzzle:
    '''Add a puzzle with a given title, creator and content.'''
    puzzle = Puzzle(title=title, creator=creator, content=content)
    db.session.add(puzzle)
    if not getattr(config.current_config, 'COMMITS_DISABLED', False):
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

def search_puzzles(query=None, rating=None, date=None, completed=None, play_count=None, following=None, sort_by='date', order='desc'):
    '''Retrieves puzzles given filters. In particular, returns the query that will result in the list of puzzles matching the filters.'''
    result = Puzzle.query
    if query:
        result = result.join(User, Puzzle.creatorID==User.id).filter(Puzzle.title.regexp_match(query) | User.name.regexp_match(query))
    result = result.outerjoin(Rating, Puzzle.id==Rating.puzzleID).group_by(Puzzle.id)
    if rating:
        result = result.having(func.coalesce(func.avg(Rating.rating), 0).between(rating[0],rating[1]))
    if date:
        result = result.filter(Puzzle.dateCreated.between(date[0], date[1]))
    if play_count:
        result = result.filter(Puzzle.play_count.between(play_count[0], play_count[1]))
    result = result.outerjoin(LeaderboardRecord, LeaderboardRecord.puzzleID==Puzzle.id)
    if completed:
        if completed[1] is True:
             result = result.filter(LeaderboardRecord.userID==completed[0].id)
        else:
            exclude = list(result.filter(LeaderboardRecord.userID==completed[0].id).with_entities(Puzzle.id).all())
            exclude = [i[0] for i in exclude]
            result = result.filter(Puzzle.id.not_in(exclude))
    if following and following[1]:
        include = list(Follow.query.filter(Follow.followerID == following[0].id).with_entities(Follow.userID).all())
        include = [i[0] for i in include]
        result = result.filter(Puzzle.creatorID.in_(include))

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

def get_following_rated(user):
    result = Puzzle.query
    
    user_following_ids = [i.userID for i in user.following]

    result = result.join(Rating, Puzzle.id==Rating.puzzleID).join(User, User.id==Rating.userID)
    result = result.filter(Rating.userID.in_(user_following_ids))
    result = result.order_by(desc(Rating.dateRated)).limit(10).add_entity(Rating.dateRated).add_entity(User)
    result = result.all()
    
    result_with_type = [(puzzle, 'rated') for puzzle in result]
    return result_with_type

def get_following_puzzles(user):
    result = Puzzle.query
    
    user_following_ids = [i.userID for i in user.following]

    result = result.filter(Puzzle.creatorID.in_(user_following_ids))
    result = result.order_by(desc(Puzzle.dateCreated)).limit(10).all()
    result_with_type = [(puzzle, 'created') for puzzle in result]

    return result_with_type

def create_feed(user):
    recent_puzzles = [ (p[0], p[0].dateCreated, p[1], p[0].creator) for p in get_following_puzzles(user)]
    recent_rated_puzzles = [ (p[0][0], p[0][1], p[1], p[0][2]) for p in get_following_rated(user)]

    print(recent_puzzles)
    
    all_puzzles = recent_puzzles + recent_rated_puzzles

    feed = sorted(all_puzzles, key=lambda x: x[1], reverse=True)
    
    return feed
