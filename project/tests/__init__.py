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

    numUsers = 100
    numPuzzles = 300
    numScores = 95
    numRatings = 90

    identifier = '$'

    def __init__(self, app, db):
        self.app = app
        self.db = db
        self.meta = sqlalchemy.MetaData()
        self.meta.reflect(bind=db.engine)
        self.numUsers = TestObject.numUsers
        self.numPuzzles = TestObject.numPuzzles
        self.numScores = TestObject.numScores
        self.numRatings = TestObject.numRatings
        self.identifier = TestObject.identifier
    
    def commit_db(self):
        if not Config.TESTING:
            self.db.session.commit()
    
    def clear_db(self, all=False):
        self.db.session.remove()
        if all:
            for table in reversed(self.meta.sorted_tables):
                self.db.session.query(table).delete()
            self.commit_db()
            return
        delete_users = [u.id for u in User.query.filter(~(User.name.contains(self.identifier))).all()]
        delete_puzzles = [p.id for p in Puzzle.query.filter(~(Puzzle.title.contains(self.identifier))).all()]
        for table in reversed(self.meta.sorted_tables):
            attrs = [a.name for a in table._columns.values()]
            if 'puzzleID' in attrs:
                self.db.session.query(table).filter(table.c.puzzleID.in_(delete_puzzles)).delete()
            if 'userID' in attrs:
                self.db.session.query(table).filter(table.c.userID.in_(delete_users)).delete()
            if 'followerID' in attrs:
                self.db.session.query(table).filter(table.c.followerID.in_(delete_users)).delete()
            if table.name == 'Users':
                self.db.session.query(table).filter(table.c.id.in_(delete_users)).delete()
            if table.name == 'Puzzles':
                self.db.session.query(table).filter(table.c.id.in_(delete_puzzles)).delete()
        self.commit_db()
    
    def add_test_client(self, client):
         self.client = client

    def generate_users(self):
        for i in range(self.numUsers):
                user_utils.add_user(self.identifier + "GENERATED_USER_" + str(i), "123")

    def get_random_user(self) -> User:
        return self.db.session.query(User).limit(1).offset(random.randint(0, self.numUsers - 1)).first()
    
    def generate_puzzles(self):
         for i in range(self.numPuzzles):
                user = self.get_random_user()
                content = ''.join(random.choice(string.ascii_uppercase) for _ in range(10))
                puzzle = puzzle_utils.add_puzzle(title = self.identifier + "GENERATED_PUZZLE_" + str(i), creator=user, content=content)
                puzzle.dateCreated = random_date(datetime.datetime(year=2000, month=1, day=1), datetime.datetime.now())
                self.commit_db()

    def get_random_puzzle(self) -> Puzzle:
         return self.db.session.query(Puzzle).limit(1).offset(random.randint(0, self.numPuzzles - 1)).first()
    
    def generate_scores(self):
         for i in range(self.numPuzzles):
            puzzle = self.get_random_puzzle()
            for j in range(self.numScores):
                user = self.get_random_user()
                if not puzzle.has_record(user):
                    puzzle.add_record(user, random.randrange(1, 1000))
                    puzzle.get_record(user).dateSubmitted = random_date(puzzle.dateCreated, datetime.datetime(year=2500, month=12, day=31))
                    self.commit_db()

    def generate_ratings(self):
         for i in range(self.numPuzzles):
            puzzle = self.get_random_puzzle()
            for j in range(min(puzzle.play_count, self.numRatings)):
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

from project import app, db

app_context = app.app_context()
app_context.push()
db.create_all()

#disable & reenable commit for batch commit
start = datetime.datetime.now()
print('Generating standard test database...')
Config.TESTING = True
t = TestObject(app, db)
t.generate_users()
t.generate_puzzles()
t.generate_scores()
t.generate_ratings()
Config.TESTING = False
db.session.commit()
print('Done.')
app_context.pop()
elapsed = str((datetime.datetime.now()-start).total_seconds())
print(f'Time elapsed: {float(elapsed):.3f}s')
