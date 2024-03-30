import json
import os
import hashlib
from flask import session
from config import PATH


def load_users():
    users_path = os.path.join(PATH, 'users', 'users.json')
    with open(users_path, 'r') as f:
        return json.load(f)   

def write_users(users):
    users_path = os.path.join(PATH, 'users', 'users.json')
    with open(users_path, 'w') as f:
        json.dump(users, f) 

def login_user(username, password):
    users = load_users()

    # verify username and password are in registered users
    for user in users['users']:
        if user['username'] == username and user['password'] == password:
            session['username'] = username
            return True
    return False

def register_user(username, password):
    users = load_users()

    # check if username already exists
    for user in users['users']:
        if user['username'] == username:
            return False

    # if not, append new user
    users['users'].append({
        'username': username,
        'password': password
    })
    write_users(users)

    return True

def get_user_id(username):
    return hashlib.sha256(username.encode()).hexdigest()