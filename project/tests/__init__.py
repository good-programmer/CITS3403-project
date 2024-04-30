import sqlalchemy

from flask import url_for

from project.blueprints.models import User, Follow, Puzzle
from project.utils import user_utils, puzzle_utils, route_utils as route

from project.config import Config

import random
import string
import datetime

def random_date(start, end):
    return start + (end - start) * random.random()

class TestObject:

    numUsers = 5
    numPuzzles = 10
    numScores = 5
    numRatings = 3

    def __init__(self, app, db):
        self.app = app
        self.db = db
    
    def commit_db(self):
        if not Config.TESTING:
            self.db.session.commit()
        #self.db.session.commit()
    
    def add_test_client(self, client):
         self.client = client

    def generate_users(self):
        for i in range(TestObject.numUsers):
                user_utils.add_user("GENERATED_USER_" + str(i), "123")

    def get_random_user(self) -> User:
        return self.db.session.query(User).order_by(sqlalchemy.func.random()).first()
    
    def generate_puzzles(self):
         for i in range(TestObject.numPuzzles):
                user = self.get_random_user()
                content = ''.join(random.choice(string.ascii_uppercase) for _ in range(10))
                puzzle = puzzle_utils.add_puzzle(title = "GENERATED_PUZZLE_" + str(i), creator=user, content=content)
                puzzle.dateCreated = random_date(datetime.datetime(year=2000, month=1, day=1), datetime.datetime.now())
                self.commit_db()

    def get_random_puzzle(self) -> Puzzle:
         return self.db.session.query(Puzzle).order_by(sqlalchemy.func.random()).first()
    
    def generate_scores(self):
         for i in range(TestObject.numPuzzles):
            puzzle = self.get_random_puzzle()
            for j in range(TestObject.numScores):
                user = self.get_random_user()
                if not puzzle.has_record(user):
                    puzzle.add_record(user, random.randrange(1, 1000))
                    puzzle.get_record(user).dateSubmitted = random_date(puzzle.dateCreated, datetime.datetime(year=2500, month=12, day=31))
                    self.commit_db()

    def generate_ratings(self):
         for i in range(TestObject.numPuzzles):
            puzzle = self.get_random_puzzle()
            for j in range(min(puzzle.play_count, TestObject.numRatings)):
                user = self.get_random_user()
                while not puzzle.has_record(user):
                    user = self.get_random_user()
                if not puzzle.has_rating(user):
                    puzzle.add_rating(user, random.randrange(0, 10) / 2)
                    if puzzle.get_record(user) is None:
                        print(user.id, user.name)
                        print(puzzle.has_record(user))
                        print(puzzle.get_record(user))
                    puzzle.get_rating(user).dateRated = random_date(puzzle.get_record(user).dateSubmitted, datetime.datetime(year=3000, month=12, day=31))
                    self.commit_db()

    def register(self, username, password, confirmpassword=None):
        if not confirmpassword: confirmpassword=password
        return self.client.post(url_for(route.register), 
                                data=dict(username=username,password=password,confirmpassword=confirmpassword), follow_redirects=True)
    
    def login(self, username, password):
        return self.client.post(url_for(route.login), 
                                data=dict(username=username,password=password,remember=True), follow_redirects=True)

    def logout(self):
        return self.client.get(url_for(route.logout), follow_redirects=True)