from flask import Blueprint, request, render_template, jsonify, json, url_for, redirect, abort
from .models import db, Puzzle
from flask_login import login_required, current_user

from ..utils import game_utils, auth_utils, puzzle_utils, route_utils as route

import datetime

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
            "dateCreated": puzzle.dateCreated.ctime(),
            "scores": [{"id": s.userID, "name": s.user.name, "score": s.score, "dateSubmitted": s.dateSubmitted.ctime()} for s in puzzle.scores],
            "average_score": puzzle.average_score,
            "average_rating": puzzle.average_rating
        }
        if current_user.is_authenticated:
            if puzzle.has_rating(current_user):
                r = puzzle.get_rating(current_user)
                data['rated'] = {"rating": r.rating, "dateRated": r.dateRated.ctime()}
            if puzzle.has_record(current_user):
                s = puzzle.get_record(current_user)
                data['score'] = {"score": s.score, "dateSubmitted": s.dateSubmitted.ctime()}
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
            "average_rating": p.average_rating
        }
    page_size = 10
    
    page = request.args.get('page', 1)
    page = int(page) - 1 if page.isdigit() else 0

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

        data = [f(p) for p in data.limit(page_size).offset(page*page_size).all()]

    return data