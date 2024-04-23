from datetime import datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000), unique=True)
    password = db.Column(db.String(100))

    following = db.relationship("Follow", back_populates="follower", foreign_keys='Follow.followerID')
    followers = db.relationship("Follow", back_populates="user", foreign_keys='Follow.userID')
    puzzles = db.relationship("Puzzle", back_populates="creator")
    scores = db.relationship("LeaderboardRecord", back_populates="user")

    def follow_user(self, user):
        follow = Follow(userID=user.id, followerID=self.id)
        db.session.add(follow)
        db.session.commit()    
    
    def is_following(self, user):
        return user.id in [u.userID for u in self.following]

    def unfollow_user(self, user):
        if self.is_following(user):
                db.session.query(Follow).filter( (Follow.followerID==self.id) & (Follow.userID==user.id) ).delete()
                db.session.commit()
                return True
        return False

class Puzzle(db.Model):
    __tablename__ = 'Puzzles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(1000))
    creatorID = db.Column(db.Integer, db.ForeignKey('Users.id'))
    creator = db.relationship("User", foreign_keys=[creatorID], back_populates="puzzles")
    dateCreated = db.Column(db.DateTime)
    content = db.Column(db.Text)

    scores = db.relationship("LeaderboardRecord", back_populates="puzzle")
     
    def __init__(self, title, creator, content):
        self.title = title
        self.creatorID = creator.id
        self.dateCreated = datetime.now()
        self.content = content
    
    def record_score(self, user, score):
        score = LeaderboardRecord(user, self, score)
        db.session.add(score)
        db.session.commit()

    def has_score(self, user):
         return user.id in [u.userID for u in self.scores]
    
    def update_score(self, user, score):
         record = db.session.query(LeaderboardRecord).filter( (LeaderboardRecord.userID==user.id) & (LeaderboardRecord.puzzleID==self.id) ).first()
         if record:
            record.score = score
            return True
         

class Rating(db.Model):
    __tablename__ = "Ratings"
    userID = db.Column(db.Integer, db.ForeignKey('Users.id'), primary_key=True)
    puzzleID = db.Column(db.Integer, db.ForeignKey('Puzzles.id'), primary_key=True)
    rating = db.Column(db.Float)
    dateRated = db.Column(db.DateTime)

class LeaderboardRecord(db.Model):
    __tablename__ = "Leaderboard"
    userID = db.Column(db.Integer, db.ForeignKey('Users.id'), primary_key=True)
    puzzleID = db.Column(db.Integer, db.ForeignKey('Puzzles.id'), primary_key=True)
    user = db.relationship("User", foreign_keys=[userID], back_populates="scores")
    puzzle = db.relationship("Puzzle", foreign_keys=[puzzleID], back_populates="scores")
    score = db.Column(db.Integer)
    dateSubmitted = db.Column(db.DateTime)

    def __init__(self, user, puzzle, score):
         self.userID = user.id
         self.puzzleID = puzzle.id
         self.score = score
         self.dateCreated = datetime.now()

class Follow(db.Model):
     __tablename__ = "Followers"
     followerID = db.Column(db.Integer, db.ForeignKey('Users.id'), primary_key=True)
     userID = db.Column(db.Integer, db.ForeignKey('Users.id'), primary_key=True)
     follower = db.relationship("User", back_populates="following", foreign_keys=[followerID])
     user = db.relationship("User", back_populates="followers", foreign_keys=[userID])