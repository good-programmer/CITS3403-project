from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from . import db
from flask_login import login_user, login_required, logout_user

def login():
    return render_template('login.html')
                           
def register():
    return render_template('register.html')

def login_post():
    name = request.form.get('username')
    password = request.form.get('password')
    remember = request.form.get('remember')

    user = User.query.filter_by(name=name).first()

    if user and check_password_hash(user.password, password):
        login_user(user, remember=remember)
        return redirect(url_for('profile'))
    
    flash('Incorrect username or password')
    return redirect(url_for('login'))

def register_post():
    name = request.form.get('username')
    password = request.form.get('password')
    confirm = request.form.get('confirmpassword')

    user = User.query.filter_by(name=name).first() 

    if user:
        flash('Username already exists')
        return redirect(url_for('register'))
    
    if len(name) < 3:
        flash('Username must be 3 characters or longer')
        return redirect(url_for('register'))
    
    if len(password) < 4:
        flash('Password must be 4 characters or longer')
        return redirect(url_for('register'))
    
    if password != confirm:
        flash('Passwords do not match')
        return redirect(url_for('register'))
    
    new_user = User(name=name, password=generate_password_hash(password))

    db.session.add(new_user)
    db.session.commit()

    print('added new user ' + name)
    return redirect(url_for('login'))

@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))