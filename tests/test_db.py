from datetime import datetime
import unittest

from sqlalchemy import exc

from tests import TestObject, app

from project.blueprints.models import db, User, Follow, Puzzle, LeaderboardRecord, Rating

from project.utils import user_utils, puzzle_utils


class UserModelCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app_context = app.app_context()
        cls.app_context.push()
        cls.t = TestObject(app, db)
        return super().setUpClass()

    def tearDown(self):
        self.t.clear_db()
    
    @classmethod
    def tearDownClass(cls) -> None:
        cls.app_context.pop()
        return super().tearDownClass()

    def test_name_unique(self):
        '''
        Tests that only distinct usernames can exist in the User table
        '''
        user_utils.add_user("MAIN_USER", "132131")
        self.assertRaises(exc.IntegrityError, user_utils.add_user, "MAIN_USER", "789")

    def test_follow_integrity(self):
        '''
        Tests the integrity of the database (in particular, the unique constraint).
        \nTests that the follow and unfollow methods of User work as expected.
        '''
        current_user = user_utils.add_user("MAIN_USER", "132131")
        u2 = user_utils.add_user("TEST2", "123")
        u2.follow_user(current_user)

        self.assertRaises(exc.IntegrityError, u2.follow_user, current_user)
        db.session.rollback()
        self.assertTrue(u2.unfollow_user(current_user))
        self.assertFalse(u2.unfollow_user(current_user))

    def test_follow(self):
        '''
        Tests that the relationship between User and Follow ORMs is correct and appends followers correctly.
        \nTests the is_following method of User
        '''
        current_user = user_utils.add_user("MAIN_USER", "132131")
        
        for i in range(20):
            user_utils.add_user("TEST_FOLLOWER" + str(i), "123").follow_user(current_user)

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
    @classmethod
    def setUpClass(cls) -> None:
        cls.app_context = app.app_context()
        cls.app_context.push()
        cls.t = TestObject(app, db)

        return super().setUpClass()
    
    def setUp(self):
        pass

    def tearDown(self):
        self.t.clear_db()
    
    @classmethod
    def tearDownClass(cls) -> None:
        cls.app_context.pop()
        return super().tearDownClass()
    
    def test_create(self):
        '''
        Tests the relationship between User and Puzzle in the ORM.
        \nTests that when a puzzle is created, its details are accurate.
        '''
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
        '''
        Tests *_record methods of User for correctness and integrity.
        '''
        puzzle = self.t.get_random_puzzle()
        user = user_utils.add_user("MAIN_USER", "132131")
        before = puzzle.scores.copy()

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
        '''
        Tests *_rating methods of User for correctness and integrity.
        '''
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
        '''
        Tests the average properties of Puzzle.
        \nTests that average_score is equivalent to the sum of scores divided by the number.
        \nTests that average_rating is equivalent to the sum of ratings divided by the number.
        \nTests that updating with new data is correctly reflected in a change in average.
        '''
        puzzle = self.t.get_random_puzzle()
        while len(puzzle.scores) == 0 or len(puzzle.ratings) == 0:
            puzzle = self.t.get_random_puzzle()
        
        user = user_utils.add_user("MAIN_USER", "132131")

        scores = db.session.query(LeaderboardRecord).filter_by(puzzleID=puzzle.id).all()
        s, l = sum(s.score for s in scores), len(scores)
        avg1 = s / l
        self.assertEqual(avg1, puzzle.average_score)
        puzzle.add_record(user, 1000)
        avg1 = (s + 1000) / (l + 1)
        self.assertEqual(avg1, puzzle.average_score)

        ratings = db.session.query(Rating).filter_by(puzzleID=puzzle.id).all()
        r, l = sum(r.rating for r in ratings), len(ratings)
        avg1 = r / l
        self.assertEqual(avg1, puzzle.average_rating)
        puzzle.add_rating(user, 5)
        avg1 = (r + 5) / (l + 1)
        self.assertEqual(avg1, puzzle.average_rating)

if __name__ == '__main__':
    unittest.main(verbosity=2)