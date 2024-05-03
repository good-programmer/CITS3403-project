from flask import Blueprint, request, render_template, jsonify, json, url_for, redirect, abort
from .models import db, Puzzle
from flask_login import login_required, current_user

from ..utils import game_utils, auth_utils, puzzle_utils, route_utils as route

import datetime, re

game = Blueprint('game', __name__)

@game.route('/wordGame', methods=['GET', 'POST'])
def wordGame():
    if request.method == 'POST':
        user_input = request.form['userInput']
        is_valid = game_utils.validate_input(user_input)
        print(f"'{user_input}': {is_valid}")    
        return jsonify(is_valid=is_valid)
    else:
        return render_template('wordGame.html')
    
@game.route('/wordGame/solve', methods=['POST'])
def solve():
    data = json.loads(request.data)
    submittedWords = data['submittedWords']
    score = game_utils.verify_score(submittedWords)
    print(data)
    print(f"Score: {score}")
    return data

@game.route('/puzzle/create', methods=['GET','POST'])
def submitpuzzle():
    if not current_user.is_authenticated:
        abort(401)
    if request.method == 'POST':
        fget = request.form.get
        puzzlename, content = fget('puzzlename'), fget('puzzle')
        content = content.lower()
        if auth_utils.validate_puzzle_submit(content):
            puzzle_utils.add_puzzle(puzzlename, current_user, content)
            print("Added:" + puzzlename)
            return redirect(url_for(route.index))
        else:
            return render_template('submitpuzzle.html')
    else:
        return render_template('submitpuzzle.html')
    
@game.route('/puzzle/<puzzleid>', methods=['GET'])
def getpuzzle(puzzleid):
    '''
    Retrieves a puzzle's information by id. This includes title, content, creatorID, scores, and average score and rating.
    \nIf the user is authenticated, also returns that user's score and rating for the puzzle (if any).
    '''
    puzzle = puzzle_utils.get_puzzle(id=puzzleid)
    if puzzle:
        data = {
            "id": puzzle.id,
            "title": puzzle.title,
            "content": puzzle.content,
            "creatorID": puzzle.creatorID,
            "dateCreated": str(puzzle.dateCreated),
            "scores": [{"id": s.userID, "name": s.user.name, "score": s.score, "dateSubmitted": str(s.dateSubmitted)} for s in puzzle.scores],
            "average_score": puzzle.average_score,
            "average_rating": puzzle.average_rating
        }
        if current_user.is_authenticated:
            if puzzle.has_rating(current_user):
                r = puzzle.get_rating(current_user)
                data['rated'] = {"rating": r.rating, "dateRated": str(r.dateRated)}
            if puzzle.has_record(current_user):
                s = puzzle.get_record(current_user)
                data['score'] = {"score": s.score, "dateSubmitted": str(s.dateSubmitted)}
        return data
    abort(404)

@game.route('/puzzle/<puzzleid>/rate', methods=['POST'])
def ratepuzzle(puzzleid):
    '''
    Allows an authenticated user to rate a puzzle given they have submitted a score.
    \nReturns the puzzle's average rating (after adding the user's).
    '''
    if not current_user.is_authenticated:
        abort(401)
    puzzle = puzzle_utils.get_puzzle(id=puzzleid)
    if puzzle:
        if puzzle.has_record(current_user):
            if puzzle.has_rating(current_user):
                puzzle.update_rating(current_user, request.values['rating'])
            else:
                puzzle.add_rating(current_user, request.values['rating'])
            return {"average_rating": puzzle.average_rating}
        abort(401)
    abort(404)

@game.route('/puzzle/search', methods=['GET'])
@game.route('/puzzle/search/<trend>', methods=['GET'])
def searchpuzzle(trend=None):
    def f(p):
        return {
            "id": p.id,
            "title": p.title,
            "creatorID": p.creatorID,
            "creator": p.creator.name,
            "play_count": p.play_count,
            "average_rating": p.average_rating,
            "dateCreated": str(p.dateCreated),
            "highscore": p.highest_score
        }
    
    def standardize(s:str):
        '''Turn a search query into a regex for database search'''
        s = s.lower()
        common = ['_', ' ']
        for i in common:
            s = s.replace(i, '.*')
        return '(?i)' + s
    
    def setdefaults(lst, into):
        for i in range(len(lst)):
            if lst[i]:
                into[i] = lst[i]
        return into

    #regex for validating search params
    def isfloat(s):
        return re.match(r'^-?\d+(\.\d+)?$', s) is not None
    
    def isdate(s):
        return re.match(r'^\d{4}-\d{2}-\d{2}$', s) is not None
    
    page_size = request.args.get('page_size', '10')
    page_size = int(page_size) if page_size.isdigit() else 10
    page = request.args.get('page', '1')
    page = int(page) if page.isdigit() else 1

    data = None

    if trend:
        match trend:
            case 'recent':
                data = Puzzle.query.order_by(db.desc(Puzzle.dateCreated))
            case 'hot':
                t = datetime.datetime.now() - datetime.timedelta(weeks=1)
                data = Puzzle.query.where(Puzzle.dateCreated > t).order_by(db.desc(Puzzle.play_count))
            case 'popular':
                data = Puzzle.query.order_by(db.desc(Puzzle.play_count))
            case _:
                abort(404)
    else:
        query = standardize(request.args.get('query', '.*'))

        rating = setdefaults(request.args.get('rating', '0-5').split('-'), ['0', '5'])
        rating = [(float(i) if isfloat(i) else 0) for i in rating]

        date = request.args.get('after', '0000-01-01'), request.args.get('to', '9999-01-01')
        date = [(i if isdate(i) else '0000-01-01') for i in date]

        completed = request.args.get('completed', None)
        if completed and current_user.is_authenticated:
            completed = (current_user, True if completed.lower() == 'true' else False)
        else:
            completed = None

        play_count = setdefaults(request.args.get('play_count', '0').split('-'), ['0', '999999'])
        play_count = [(float(i) if isfloat(i) else 0) for i in play_count]

        sort_by = request.args.get('sort_by', 'date').lower()
        if sort_by not in ['date', 'play_count', 'highscore', 'rating', 'a-z']:
            sort_by = 'date'
        
        order = request.args.get('order', 'desc')
        if order not in ['desc', 'asc']:
            order = 'desc'

        data = puzzle_utils.search_puzzles(query=query, rating=rating, date=date, completed=completed, play_count=play_count, sort_by=sort_by, order=order)
    
    page = data.paginate(page=page, per_page=page_size, error_out=True)
    data = [f(p) for p in page.items]
    
    return {"puzzles": data, "pages": page.pages, "count": page.total}