from flask import Blueprint, render_template
from flask_login import login_required, current_user
from ..utils import route_utils as route

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html', route=route)

@main.route('/aboutus')
def about_us():
    return render_template('aboutus.html', route=route)

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', route=route, name=current_user.name)