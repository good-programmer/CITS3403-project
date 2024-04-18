from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

class Puzzle(db.Model):
    __tablename__ = 'Puzzles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(1000))
    authorID = db.Column(db.Integer, db.ForeignKey('Users.id'))
    author = db.relationship("User", backref=db.backref("Users", uselist=False))
    dateCreated = db.Column(db.DateTime)
    content = db.Column(db.Text)

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
    score = db.Column(db.Integer)
    dateSubmitted = db.Column(db.DateTime)

class Follow(db.Model):
     __tablename__ = "Followers"
     userID = db.Column(db.Integer, db.ForeignKey('Users.id'), primary_key=True)
     follows = db.Column(db.Integer, db.ForeignKey('Users.id'), primary_key=True)