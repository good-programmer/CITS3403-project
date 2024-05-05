import sqlalchemy

from flask import url_for

from project.blueprints.models import User, Puzzle
from project.utils import user_utils, puzzle_utils, route_utils as route

from project.config import Config, PATH

import os
import random
import string
import datetime

def random_date(start, end):
    return start + (end - start) * random.random()

words = os.path.join(PATH, 'utils', 'words_dict')
with open(words, 'r') as f:
    valid_words = tuple(word.strip() for word in f)

def random_word():
    return random.choice(valid_words)

def random_username(i):
    return random_word().capitalize() + random_word().capitalize() + str(random.randint(1, 100))

def random_puzzletitle(i):
    return ' '.join([random_word().capitalize() for i in range(random.randint(3,6))])

def ordered_username(i):
    return "GENERATED_USER_" + str(i)

def ordered_puzzletitle(i):
    return "GENERATED_PUZZLE_" + str(i)

class TestObject:

    numUsers = 500
    numPuzzles = 800
    numScores = 400
    numRatings = 350

    generate_username = random_username
    generate_puzzletitle = random_puzzletitle

    identifier = ''

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
        self.generate_username = TestObject.generate_username
        self.generate_puzzletitle = TestObject.generate_puzzletitle
    
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
                user_utils.add_user(self.identifier + self.generate_username(i), "123")

    def get_random_user(self) -> User:
        return self.db.session.query(User).limit(1).offset(random.randint(0, self.numUsers - 1)).first()
    
    def generate_puzzles(self):
         for i in range(self.numPuzzles):
                user = self.get_random_user()
                content = ''.join(random.choice(string.ascii_uppercase) for _ in range(10))
                puzzle = puzzle_utils.add_puzzle(title = self.identifier + self.generate_puzzletitle(i), creator=user, content=content)
                puzzle.dateCreated = random_date(datetime.datetime(year=2000, month=1, day=1), datetime.datetime.now())
                self.commit_db()

    def get_random_puzzle(self) -> Puzzle:
         return self.db.session.query(Puzzle).limit(1).offset(random.randint(0, self.numPuzzles - 1)).first()
    
    def generate_scores(self):
         for puzzle in Puzzle.query.all():
            for user in User.query.order_by(sqlalchemy.func.random()).limit(random.randint(0,self.numScores)):
                puzzle.add_record(user, random.randrange(1, 1000))
                puzzle.get_record(user).dateSubmitted = random_date(puzzle.dateCreated, datetime.datetime(year=2500, month=12, day=31))
                self.commit_db()

    def generate_ratings(self):
         for puzzle in Puzzle.query.all():
            for j in range(puzzle.play_count):
                user = random.choice(puzzle.scores).user
                if puzzle.has_rating(user):
                    continue
                puzzle.add_rating(user, random.randrange(0, 10) / 2)
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

def create_test_db(msg='Generating standard test database...'):
    from project import app, db

    app_context = app.app_context()
    app_context.push()
    db.create_all()

    #disable & reenable commit for batch commit
    start = datetime.datetime.now()
    print(msg)
    Config.TESTING = True
    t = TestObject(app, db)
    print('Users...')
    t.generate_users()
    print('Puzzles...')
    t.generate_puzzles()
    print('Scores...')
    t.generate_scores()
    print('Ratings...')
    t.generate_ratings()
    Config.TESTING = False
    db.session.commit()
    print('Done.')
    app_context.pop()
    elapsed = str((datetime.datetime.now()-start).total_seconds())
    print(f'Time elapsed: {float(elapsed):.3f}s')