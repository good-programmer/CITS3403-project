from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000), unique=True)
    password = db.Column(db.String(100))

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
    authorID = db.Column(db.Integer, db.ForeignKey('Users.id'))
    author = db.relationship("User", foreign_keys=[authorID], backref=db.backref("puzzles"))
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
    puzzle = db.relationship("Puzzle", foreing_keys=[puzzleID], backref=db.backref("scores"))
    user = db.relationship("User", foreing_keys=[userID], backref=db.backref("scores"))
    score = db.Column(db.Integer)
    dateSubmitted = db.Column(db.DateTime)

class Follow(db.Model):
     __tablename__ = "Followers"
     followerID = db.Column(db.Integer, db.ForeignKey('Users.id'), primary_key=True)
     userID = db.Column(db.Integer, db.ForeignKey('Users.id'), primary_key=True)
     follower = db.relationship("User", foreign_keys=[followerID], backref=db.backref("following"))
     user = db.relationship("User", foreign_keys=[userID], backref=db.backref("followers"))