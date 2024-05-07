from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import login_user, login_required, logout_user, current_user

from ..utils import auth_utils, user_utils, route_utils as route

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=["GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for(route.profile))
    return render_template('login.html', route=route)

@auth.route('/register', methods=["GET"])             
def register():
    if current_user.is_authenticated:
        return redirect(url_for(route.profile))
    return render_template('register.html', route=route)

@auth.route('/login', methods=["POST"])
def login_post():
    fget = request.form.get
    name, password, remember = fget('username'), fget('password'), fget('remember')

    user = user_utils.verify_user(name, password)
    if user:
        login_user(user, remember=remember)
        return redirect(url_for(route.profile))
    
    flash('Incorrect username or password', 'error')
    return redirect(url_for(route.login))

@auth.route('/register', methods=["POST"])
def register_post():
    fget = request.form.get
    name, password, confirm = fget('username'), fget('password'), fget('confirmpassword')

    if user_utils.verify_user(name):
        flash('Username already exists', 'error')
        return redirect(url_for(route.register))

    res, msgs = auth_utils.validate_user_information(name, password)
    if not res:
        for msg in msgs:
            flash(msg, 'error')
        return redirect(url_for(route.register))
    
    if password != confirm:
        flash('Passwords do not match', 'error')
        return redirect(url_for(route.register))
    
    user_utils.add_user(name, password)

    #print('added new user ' + name)
    return redirect(url_for(route.login))

@auth.route('/logout')
@login_required
def logout():
    '''
    If logged in, logs out the current user.
    '''
    logout_user()
    return redirect(url_for(route.index))

@auth.route('/user/current', methods=["GET"])
def api_current_user():
    '''
    Retrieves the username and id of the current authenticated user.
    \n-id
    \n-username
    '''
    if current_user.is_authenticated:
        return user_utils.pack_user(current_user)
    else:
        return {"id": -1, "username": ""}

@auth.route('/user/<int:userid>', methods=["GET"])
def api_get_user(userid):
    '''
    Retrieves the public information of a given user by their id.
    \n-id
    \n-username
    \n-followers
    \n-following
    \n-scores
    \n-ratings
    \nIf current user is authenticated, also retrieves their followage to this user.
    '''
    user = user_utils.get_user(id=userid)
    if user:
        data = user_utils.pack_user(user)
        if current_user.is_authenticated:
            data['is_following'] = current_user.is_following(user)
        return data
    abort(404)

@auth.route('/user/follow', methods=["POST"])
def api_follow_user():
    '''
    Allows the current authenticated user to follow another user by id.
    Requires a POST request to the endpoint containing key-pair [id=userID]
    '''
    if not current_user.is_authenticated:
        abort(401)
    user = user_utils.get_user(id=request.values['id'])
    if user:
        if current_user.is_following(user):
            abort(400)
        else:
            current_user.follow_user(user)
            return [{"id": u.userID, "name": u.user.name} for u in current_user.following], 200

@auth.route('/user/unfollow', methods=["POST"])
def api_unfollow_user():
    '''
    Allows the current authenticated user to unfollow another user by id.
    Requires a POST request to the endpoint containing key-pair [id=userID]
    '''
    if not current_user.is_authenticated:
        abort(401)
    user = user_utils.get_user(id=request.values['id'])
    if user:
        if not current_user.is_following(user):
            abort(400)
        else:
            current_user.unfollow_user(user)
            return [{"id": u.userID, "name": u.user.name} for u in current_user.following], 200