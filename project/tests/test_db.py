from datetime import datetime, timezone, timedelta
import unittest

from sqlalchemy import exc

from project.tests import TestObject

from project import app
from project.blueprints.models import db, User, Follow, Puzzle, LeaderboardRecord, Rating

from project.utils import user_utils, puzzle_utils

class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_account(self):
        current_user = user_utils.add_user("MAIN_USER", "132131")
        self.assertIsNotNone(db.session.query(User).filter_by(id=current_user.id).first())
        self.assertIsNotNone(user_utils.verify_user("MAIN_USER"))
        self.assertIsNone(user_utils.verify_user("__DNE__"))
        self.assertIsNotNone(user_utils.verify_user("MAIN_USER", "132131"))
        self.assertIsNone(user_utils.verify_user("MAIN_USER", "__INCORRECT__"))
        self.assertRaises(exc.IntegrityError, user_utils.add_user, "MAIN_USER", "789")

    def test_follow_integrity(self):
        current_user = user_utils.add_user("MAIN_USER", "132131")
        u2 = user_utils.add_user("TEST2", "123")
        u2.follow_user(current_user)

        self.assertRaises(exc.IntegrityError, u2.follow_user, current_user)
        db.session.rollback()
        self.assertTrue(u2.unfollow_user(current_user))
        self.assertFalse(u2.unfollow_user(current_user))

    def test_follow(self):
        current_user = user_utils.add_user("MAIN_USER", "132131")
        
        for i in range(20):
            user_utils.add_user("TEST_FOLLOWER" + str(i), "123").follow_user(current_user)
        db.session.commit()

        f1 = db.session.query(Follow).filter_by(userID=current_user.id).all()
        f2 = db.session.query(User).filter_by(id=current_user.id).first().followers
        x = [f.follower.name for f in f1]
        y = [f.follower.name for f in f2]
        x.sort()
        y.sort()

        self.assertListEqual(x, y)

        u2 = user_utils.add_user("TEST2", "123")
        self.assertFalse(u2.is_following(current_user))
        u2.follow_user(current_user)
        self.assertTrue(u2.is_following(current_user))
        u2.unfollow_user(current_user)
        self.assertFalse(u2.is_following(current_user))
        self.assertIsNone(db.session.query(Follow).filter_by(userID=current_user.id, followerID=u2.id).first())

class PuzzleModelCase(unittest.TestCase):
    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()
        t = TestObject(app, db)
        self.t = t
        t.generate_users()
        t.generate_puzzles()
        t.generate_scores()
        t.generate_ratings()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_create(self):
        user = self.t.get_random_user()
        current_time = datetime.now()
        puzzle = puzzle_utils.add_puzzle(title = "TEST_PUZZLE", creator=user, content="QWOISAD")
        
        self.assertTrue(puzzle.title=="TEST_PUZZLE")
        self.assertTrue(puzzle.creatorID==user.id and puzzle.creator==user)
        self.assertTrue(puzzle.content=="QWOISAD")
        self.assertTrue((puzzle.dateCreated-current_time).total_seconds() < 0.1)
        self.assertIsNotNone(db.session.query(Puzzle).filter_by(id=puzzle.id,creatorID=user.id).first())
        self.assertIn(puzzle, user.puzzles)
    
    def test_score(self):
        puzzle = self.t.get_random_puzzle()
        user = user_utils.add_user("MAIN_USER", "132131")
        before = puzzle.scores.copy()

        #print(puzzle.title + ": " + str(puzzle.scores))
        #print(user.name + ": " + str(user.scores))

        self.assertFalse(puzzle.has_record(user))
        puzzle.add_record(user, 10)
        self.assertRaises(exc.IntegrityError, puzzle.add_record, user, 70)
        db.session.rollback()
        self.assertRaises(AssertionError, self.assertListEqual, before, puzzle.scores)
        self.assertTrue(puzzle.has_record(user))
        self.assertEqual(puzzle.get_record(user).score, 10)
        self.assertIn(puzzle.get_record(user), user.scores)
        self.assertIn(puzzle.get_record(user), puzzle.scores)
        self.assertIsNotNone(user.get_record(puzzle))
        self.assertEqual(user.get_record(puzzle).score, puzzle.get_record(user).score)
        puzzle.update_record(user, 20)
        self.assertEqual(puzzle.get_record(user).score, 20)
        self.assertEqual(user.get_record(puzzle).score, puzzle.get_record(user).score)
        puzzle.remove_record(user)
        self.assertFalse(puzzle.has_record(user))
        self.assertIsNone(user.get_record(puzzle))
        self.assertListEqual(before, puzzle.scores)
    
    def test_rating(self):
        puzzle = self.t.get_random_puzzle()
        user = user_utils.add_user("MAIN_USER", "132131")
        before = puzzle.ratings.copy()

        self.assertFalse(puzzle.has_rating(user))
        puzzle.add_rating(user, 3.5)
        self.assertRaises(exc.IntegrityError, puzzle.add_rating, user, 1.0)
        db.session.rollback()
        self.assertRaises(AssertionError, self.assertListEqual, before, puzzle.ratings)
        self.assertTrue(puzzle.has_rating(user))
        self.assertEqual(puzzle.get_rating(user).rating, 3.5)
        self.assertIn(puzzle.get_rating(user), user.ratings)
        self.assertIn(puzzle.get_rating(user), puzzle.ratings)
        self.assertIsNotNone(user.get_rating(puzzle))
        self.assertEqual(user.get_rating(puzzle).rating, puzzle.get_rating(user).rating)
        puzzle.update_rating(user, 2.5)
        self.assertEqual(puzzle.get_rating(user).rating, 2.5)
        self.assertEqual(user.get_rating(puzzle).rating, puzzle.get_rating(user).rating)
        puzzle.remove_rating(user)
        self.assertFalse(puzzle.has_rating(user))
        self.assertIsNone(user.get_rating(puzzle))
        self.assertListEqual(before, puzzle.ratings)
    
    def test_averages(self):
        puzzle = self.t.get_random_puzzle()
        while len(puzzle.scores) == 0 or len(puzzle.ratings) == 0:
            puzzle = self.t.get_random_puzzle()

        scores = db.session.query(LeaderboardRecord).filter_by(puzzleID=puzzle.id).all()
        avg1 = sum(s.score for s in scores) / len(scores)
        avg2 = puzzle.average_score
        self.assertEqual(avg1, avg2)

        ratings = db.session.query(Rating).filter_by(puzzleID=puzzle.id).all()
        avg1 = sum(r.rating for r in ratings) / len(ratings)
        avg2 = puzzle.average_rating
        self.assertEqual(avg1, avg2)

if __name__ == '__main__':
    unittest.main(verbosity=2)