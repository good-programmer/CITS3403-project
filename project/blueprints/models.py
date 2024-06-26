from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from project import db

from project import config

def commit():
    if not getattr(config.current_config, 'COMMITS_DISABLED', False):
        db.session.commit()
        
'''Many-to-many relationship between User and Leaderboard that stores User-Puzzle ratings'''
class Rating(db.Model):
    __tablename__ = "Ratings"
    userID = db.Column(db.Integer, db.ForeignKey('Users.id'), primary_key=True)
    puzzleID = db.Column(db.Integer, db.ForeignKey('Puzzles.id'), primary_key=True)
    user = db.relationship("User", foreign_keys=[userID], back_populates="ratings")
    puzzle = db.relationship("Puzzle", foreign_keys=[puzzleID], back_populates="ratings")
    rating = db.Column(db.Float, nullable=False)
    dateRated = db.Column(db.DateTime)

    def __repr__(self):
        return f'({self.puzzle.title}, {self.user.name}, {self.rating})'
    
    def __init__(self, user, puzzle, rating):
        self.userID = user.id
        self.puzzleID = puzzle.id
        self.rating = rating
        self.dateRated = datetime.now()

'''Many-to-many relationship between User and Leaderboard that stores User-Puzzle scores'''
class LeaderboardRecord(db.Model):
    __tablename__ = "Leaderboard"
    userID = db.Column(db.Integer, db.ForeignKey('Users.id'), primary_key=True)
    puzzleID = db.Column(db.Integer, db.ForeignKey('Puzzles.id'), primary_key=True)
    user = db.relationship("User", foreign_keys=[userID], back_populates="scores")
    puzzle = db.relationship("Puzzle", foreign_keys=[puzzleID], back_populates="scores")
    score = db.Column(db.Integer, nullable=False)
    dateSubmitted = db.Column(db.DateTime)

    def __repr__(self):
        return f'<{self.puzzle.title} | {self.user.name}, {self.score}>'

    def __init__(self, user, puzzle, score):
        self.userID = user.id
        self.puzzleID = puzzle.id
        self.score = score
        self.dateSubmitted = datetime.now()

'''Many-to-many relationship between Users that stores User-User relationship'''
class Follow(db.Model):
     __tablename__ = "Followers"
     followerID = db.Column(db.Integer, db.ForeignKey('Users.id'), primary_key=True)
     userID = db.Column(db.Integer, db.ForeignKey('Users.id'), primary_key=True)
     follower = db.relationship("User", back_populates="following", foreign_keys=[followerID])
     user = db.relationship("User", back_populates="followers", foreign_keys=[userID])

     def __repr__(self):
        return f'<{self.follower.name} -> {self.user.name}>'
     
class Puzzle(db.Model):
    __tablename__ = 'Puzzles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(1000), nullable=False)
    creatorID = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    creator = db.relationship("User", foreign_keys=[creatorID], back_populates="puzzles")
    dateCreated = db.Column(db.DateTime)
    content = db.Column(db.Text)
    play_count = db.Column(db.Integer, default=0)

    scores = db.relationship("LeaderboardRecord", back_populates="puzzle")
    ratings = db.relationship("Rating", back_populates="puzzle")

    @property
    def average_score(self) -> float:
        if self.scores and len(self.scores) > 0:
            return sum(s.score for s in self.scores) / len(self.scores)
        return 0
    
    @property
    def highest_score(self) -> float:
        if len(self.scores) > 0:
            return max(s.score for s in self.scores)
        return 0
    
    @property
    def average_rating(self) -> float:
        if self.ratings and len(self.ratings) > 0:
            return sum(r.rating for r in self.ratings) / len(self.ratings)
        return 0
    
    def __repr__(self):
        return f'<{self.id} {self.title}>'
     
    def __init__(self, title, creator, content):
        self.title = title
        self.creatorID = creator.id
        self.dateCreated = datetime.now()
        self.content = content
        self.play_count = 0
    
    def add_record(self, user, score):
        '''Adds a new score to the database'''
        score = LeaderboardRecord(user, self, score)
        db.session.add(score)
        self.play_count += 1
        commit()

    def has_record(self, user) -> bool:
        return LeaderboardRecord.query.filter_by(userID=user.id, puzzleID=self.id).first() is not None
    
    def get_record(self, user) -> LeaderboardRecord:
        return LeaderboardRecord.query.filter_by(userID=user.id, puzzleID=self.id).first()
    
    def update_record(self, user, score) -> bool:
        '''Updates a user's score. Returns True if successful, False otherwise.'''
        if self.has_record(user):
            self.get_record(user).score = score 
            commit()
            return True
        return False
    
    def remove_record(self, user) -> bool:
        '''Removes a user's score. Returns True if successful, False otherwise.'''
        if self.has_record(user):
            db.session.query(LeaderboardRecord).filter( (LeaderboardRecord.userID==user.id) & (LeaderboardRecord.puzzleID==self.id) ).delete()
            self.play_count -= 1
            commit()
            return True
        return False
    
    def add_rating(self, user, rating):
        '''Adds a new rating to the database'''
        rating = Rating(user, self, rating)
        db.session.add(rating)
        commit()

    def has_rating(self, user) -> bool:
        return Rating.query.filter_by(userID=user.id, puzzleID=self.id).first() is not None
    
    def get_rating(self, user) -> Rating:
        return Rating.query.filter_by(userID=user.id, puzzleID=self.id).first()
    
    def update_rating(self, user, rating) -> bool:
        '''Updates a user's rating. Returns True if successful, False otherwise.'''
        if self.has_rating(user):
            self.get_rating(user).rating = rating 
            commit()
            return True
        return False
    
    def remove_rating(self, user) -> bool:
        '''Removes a user's rating. Returns True if successful, False otherwise.'''
        if self.has_rating(user):
            db.session.query(Rating).filter( (Rating.userID==user.id) & (Rating.puzzleID==self.id) ).delete()
            commit()
            return True
        return False

class User(UserMixin, db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    following = db.relationship("Follow", back_populates="follower", foreign_keys='Follow.followerID')
    followers = db.relationship("Follow", back_populates="user", foreign_keys='Follow.userID')
    puzzles = db.relationship("Puzzle", back_populates="creator")
    scores = db.relationship("LeaderboardRecord", back_populates="user")
    ratings = db.relationship("Rating", back_populates="user")

    def __repr__(self):
        return f'<{self.id} {self.name}>'
    
    def __init__(self, name, password=''):
        self.name = name
        self.set_password(password, False)

    def set_password(self, password, selfcommit=True):
        self.password = generate_password_hash(password)
        if selfcommit:
            commit()
    
    def check_password(self, password):
        return check_password_hash(self.password, password)

    def follow_user(self, user):
        '''Adds a new follow relationship to the database'''
        follow = Follow(userID=user.id, followerID=self.id)
        db.session.add(follow)
        commit()    
    
    def is_following(self, user) -> bool:
        return Follow.query.filter_by(userID=user.id, followerID=self.id).first() is not None

    def unfollow_user(self, user) -> bool:
        '''Returns true if successful, false otherwise.'''
        if self.is_following(user):
                db.session.query(Follow).filter( (Follow.followerID==self.id) & (Follow.userID==user.id) ).delete()
                commit()
                return True
        return False
    
    '''User wrappers for related puzzle methods'''
    def get_record(self, puzzle) -> LeaderboardRecord:
        return puzzle.get_record(self)
    
    def rate_puzzle(self, puzzle, rating):
        return puzzle.add_rating(self, rating)
    
    def get_rating(self, puzzle) -> Rating:
        return puzzle.get_rating(self)
