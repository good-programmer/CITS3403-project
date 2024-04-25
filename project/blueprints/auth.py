from flask import Blueprint, render_template, redirect, url_for, request, flash
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
    logout_user()
    return redirect(url_for(route.index))

@auth.route('/user/current')
def getuser():
    if current_user.is_authenticated:
        return {
            "id": current_user.id,
            "username": current_user.name
        }
    else:
        return {"id": -1, "username": ""}