from flask import Blueprint, session, request, render_template, redirect, url_for
from utils.auth_utils import login_user, get_user_id, register_user


bp = Blueprint('auth', __name__, url_prefix='/')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        # credentials entered by user
        username = request.form.get('username')
        password = request.form.get('password')

        if login_user(username, password):
            session['logged_in'] = True
            session['user_id'] = get_user_id(username)
            return redirect(url_for('index.index')) # success, redirect to index
        else:
            error = 'invalid credentials'
            print(error)
    return render_template('login.html', error=error, title='Login') # failure, stay on same page

@bp.route('/logout')
def logout():
    # pop user information from session
    session.pop('logged_in', None)
    session.pop('user_id', None)
    return redirect(url_for('auth.login')) # logged out, redirect to login

@bp.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        # credentials entered by user
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # check fields are populated (prevents instantly registering NULL)
        if username and password:
            # check passwords match
            if password == confirm_password:
                # add new user to json; redirect to login
                if register_user(username, password):
                    print('Registration successful! Please log in.')
                    return redirect(url_for('auth.login')) # success, redirect to login
                else:
                    error = 'Username already exists - please try again'
                    print(error)
            else:
                error = 'Passwords do not match - please try again'
                print(error)
    return render_template('register.html', error=error, title='Register') # failure, stay on same page