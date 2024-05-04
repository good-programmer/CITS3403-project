from flask import session, flash, redirect, url_for
from ..config import PATH
import re

from . import route_utils as route

def pack_user(user) -> dict:
    '''Packs a user's public information into a dictionary'''
    return {
            "id": user.id,
            "username": user.name,
            "followers": [{"id": u.followerID, "name": u.follower.name} for u in user.followers],
            "following": [{"id": u.userID, "name": u.user.name} for u in user.following],
            "scores": [{"puzzleID": s.puzzleID, "puzzle": s.puzzle.title, "score": s.score, "dateSubmitted": str(s.dateSubmitted)} for s in user.scores],
            "ratings": [{"puzzleID": r.puzzleID, "puzzle": r.puzzle.title, "rating": r.rating, "dateRated": str(r.dateRated)} for r in user.ratings]
        }

def validate_user_information(name, password) -> tuple[bool, str]:
    '''Checks that username is >3 chars and password is >4 chars'''
    if len(name) < 3:
        return False, 'Username must be 3 characters or longer'
    
    if len(password) < 4:
        return False, 'Password must be 4 characters or longer'
    
    return True, ''
    
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
    if str_len != 10:
        flash("String is incorrect length, need to be length 10", 'error')
        return False

    # If input passes all checks, return True
    return True
