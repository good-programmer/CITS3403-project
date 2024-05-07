from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import login_user, login_required, logout_user, current_user
from project.forms import LoginForm, RegistrationForm

from ..utils import auth_utils, user_utils, route_utils as route

import json

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for(route.profile))
    
    form = LoginForm()
    if form.validate_on_submit():
        name = form.username.data
        password = form.password.data
        remember = form.remember_me.data

        user = user_utils.verify_user(name, password)
        if user:
            login_user(user, remember=remember)
            return redirect(url_for(route.user.profile, userid=user.id))

        flash('Incorrect username or password', 'error')
        return redirect(url_for('auth.login'))

    return render_template('login.html', form=form, route=route)

@auth.route('/register', methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for(route.profile))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        name = form.username.data
        password = form.password.data
        confirm_password = form.password2.data

        # Perform user registration
        if user_utils.verify_user(name):
            flash('Username already exists', 'error')
            return redirect(url_for(route.register))
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')  # Flash message for password mismatch
            return redirect(url_for(route.register))

        res, msgs = auth_utils.validate_user_information(name, password)
        if not res:
            for msg in msgs:
                flash(msg, 'error')
            return redirect(url_for(route.register))
        
        user_utils.add_user(name, password)
        return redirect(url_for(route.login))
    return render_template('register.html', form=form, route=route)

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

@auth.route('/user/<int:userid>/profile', methods=["GET"])
def page_user_profile(userid):

    user = user_utils.get_user(id=userid)
    if not user:
        abort(404)
    return render_template('profile.html', route=route, current_user=current_user, user=user_utils.pack_user(user), following=(current_user.is_following(user) if current_user.is_authenticated else True))

@auth.route('/user/follow', methods=["POST"])
def api_follow_user():
    '''
    Allows the current authenticated user to follow another user by id.
    Requires a POST request to the endpoint containing key-pair [id=userID]
    '''
    if not current_user.is_authenticated:
        abort(401)
    user = user_utils.get_user(id=request.get_json()['id'])
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
    user = user_utils.get_user(id=request.get_json()['id'])
    if user:
        if not current_user.is_following(user):
            abort(400)
        else:
            current_user.unfollow_user(user)
            return [{"id": u.userID, "name": u.user.name} for u in current_user.following], 200