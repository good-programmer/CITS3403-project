from flask import session, flash, redirect, url_for
from ..config import PATH
import re

from . import route_utils as route

def validate_user_information(name, password) -> tuple[bool, str]:
    '''Checks that username and password meet min requirements'''
    valid = True
    errors = []

    valid_username = re.compile('^\w+$')

    if not (3 <= len(name) <= 20):
        valid = False
        errors.append('Username must be between 3 and 20 characters')
    
    if not valid_username.match(name):
        valid = False
        errors.append('Username must contain only letters, numbers and _')
    
    if not len(password) >= 4:
        valid = False
        errors.append('Password must be 4 characters or longer')
    
    return valid, errors
    
# Function to check puzzle submit input string for non-alphabetical characters and length
def validate_puzzle_submit(input):
    valid = True
    errors = []

    # Regex for special characters
    alpha_chars = re.compile('^[a-zA-Z]+$')

    # Check if input contains only alphabetical characters
    if not alpha_chars.match(input):
        valid = False
        errors.append("String can only have alphabetical characters")

    # Check if input length is correct
    str_len = len(input)
    if str_len != 10:
        valid = False
        errors.append("String is incorrect length, need to be length 10")

    # If input passes all checks, return True
    return valid, errors
