import sqlalchemy

from project.blueprints.models import User, Follow, Puzzle
from project.utils import user_utils, puzzle_utils

import random
import string

class TestObject:
    def __init__(self, app, db):
        self.app = app
        self.db = db

    def generate_users(self):
        for i in range(15):
                user_utils.add_user("GENERATED_USER_" + str(i), "123")

    def get_random_user(self):
        return self.db.session.query(User).order_by(sqlalchemy.func.random()).first()
    
    def generate_puzzles(self):
         for i in range(35):
                user = self.get_random_user()
                content = ''.join(random.choice(string.ascii_uppercase) for _ in range(10))
                puzzle_utils.add_puzzle(title = "GENERATED_PUZZLE_" + str(i), creator=user, content=content)

    def get_random_puzzle(self):
         return self.db.session.query(Puzzle).order_by(sqlalchemy.func.random()).first()