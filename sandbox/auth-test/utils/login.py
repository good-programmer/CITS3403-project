import json
import os
from flask import Blueprint, request, render_template

bp = Blueprint('login', __name__, url_prefix='/login')

# get current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# construct path for json
json_path = os.path.join(current_dir, '../users/users.json')

with open(json_path, 'r') as f:
    users = json.load(f)

@bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # credentials entered by user
        username = request.form.get('username')
        password = request.form.get('password')

        # traverse json and find match
        for user in users['users']:
            if user['username'] == username and user['password'] == password:
                return render_template('home.html')
            return render_template('login.html', error='invalid credentials')

    return render_template('login.html')
