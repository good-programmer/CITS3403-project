from flask import Blueprint, request, render_template, jsonify, json
from .models import db
from flask_login import login_required, current_user

from ..utils import game_utils

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