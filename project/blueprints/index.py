from flask import Blueprint, session, render_template, redirect, url_for

bp = Blueprint('index', __name__)

@bp.route('/')
def index():
    if 'logged_in' in session:
        print(session['user_id'])
        return render_template('index.html', title='Index')
    else:
        return redirect(url_for('auth.login'))  # redirect to login page if not logged in
