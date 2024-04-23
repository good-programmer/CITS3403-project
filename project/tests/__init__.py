import sqlalchemy

from project.blueprints.models import User, Follow, Puzzle
from project.utils import user_utils, puzzle_utils

import random
import string

numUsers = 15
numPuzzles = 35
numScores = 10

class TestObject:
    def __init__(self, app, db):
        self.app = app
        self.db = db

    def generate_users(self):
        for i in range(numUsers):
                user_utils.add_user("GENERATED_USER_" + str(i), "123")

    def get_random_user(self):
        return self.db.session.query(User).order_by(sqlalchemy.func.random()).first()
    
    def generate_puzzles(self):
         for i in range(numPuzzles):
                user = self.get_random_user()
                content = ''.join(random.choice(string.ascii_uppercase) for _ in range(10))
                puzzle_utils.add_puzzle(title = "GENERATED_PUZZLE_" + str(i), creator=user, content=content)

    def get_random_puzzle(self) -> Puzzle:
         return self.db.session.query(Puzzle).order_by(sqlalchemy.func.random()).first()
    
    def generate_scores(self):
         for i in range(numPuzzles):
            puzzle = self.get_random_puzzle()
            for j in range(numScores):
                user = self.get_random_user()
                if not puzzle.has_record(user):
                    puzzle.add_record(user, random.randrange(1, 1000))