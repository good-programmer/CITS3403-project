from flask import session, flash, redirect, url_for
from ..config import PATH
import re

from . import route_utils as route

def validate_user_information(name, password):
    
    if len(name) < 3:
        flash('Username must be 3 characters or longer')
        return redirect(url_for(route.register))
    
    if len(password) < 4:
        flash('Password must be 4 characters or longer')
        return redirect(url_for(route.register))
    
# Function to check puzzle submit input string for non-alphabetical characters and length
def validate_puzzle_submit(input):
    # Regex for special characters
    alpha_chars = re.compile('^[a-zA-Z]+$')

    # Check if input contains only alphabetical characters
    if not alpha_chars.match(input):
        flash("String can only have alphabetical characters", 'error')
        return False

    # Check if input length is correct
    str_len = len(input)
    if str_len > 10 or str_len < 3:
        flash("String is incorrect length, string needs to be < 10 and > 2", 'error')
        return False

    # If input passes all checks, return True
    return True