from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db, User
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
    
    flash('Incorrect username or password')
    return redirect(url_for(route.login))

@auth.route('/register', methods=["POST"])
def register_post():
    fget = request.form.get
    name, password, confirm = fget('username'), fget('password'), fget('confirmpassword')

    if user_utils.verify_user(name):
        flash('Username already exists')
        return redirect(url_for(route.register))

    res, msg = auth_utils.validate_user_information(name, password)
    if not res:
        flash(msg)
        return redirect(url_for(route.register))
    
    if password != confirm:
        flash('Passwords do not match')
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
def currentuser():
    '''
    Retrieves the username and id of the current authenticated user.
    \n-id
    \n-username
    '''
    if current_user.is_authenticated:
        return {
            "id": current_user.id,
            "username": current_user.name
        }
    else:
        return {"id": -1, "username": ""}

@auth.route('/user/<userid>', methods=["GET"])
def getuser(userid):
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
        data = {
            "id": user.id,
            "username": user.name,
            "followers": [{"id": u.followerID, "name": u.follower.name} for u in user.followers],
            "following": [{"id": u.userID, "name": u.user.name} for u in user.following],
            "scores": [{"puzzleID": s.puzzleID, "puzzle": s.puzzle.title, "score": s.score, "dateSubmitted": str(s.dateSubmitted)} for s in user.scores],
            "ratings": [{"puzzleID": r.puzzleID, "puzzle": r.puzzle.title, "rating": r.rating, "dateRated": str(r.dateRated)} for r in user.ratings]
        }
        if current_user.is_authenticated:
            data['is_following'] = current_user.is_following(user)
        return data
    abort(404)

@auth.route('/user/follow', methods=["POST"])
def followuser():
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
def unfollowuser():
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