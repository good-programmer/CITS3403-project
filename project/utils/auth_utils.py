from flask import session, flash, redirect, url_for
from ..config import PATH

from . import route_utils as route

def validate_user_information(name, password):
    
    if len(name) < 3:
        flash('Username must be 3 characters or longer')
        return redirect(url_for(route.register))
    
    if len(password) < 4:
        flash('Password must be 4 characters or longer')
        return redirect(url_for(route.register))