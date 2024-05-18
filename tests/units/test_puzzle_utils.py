'''
pack_puzzle
add_puzzle
get_puzzle
search_puzzle
'''

import unittest, datetime

from sqlalchemy import exc

from tests import app, TestObject

from project.blueprints.models import db, Puzzle, User

from project.utils.puzzle_utils import pack_puzzle, add_puzzle, get_puzzle, search_puzzles, get_following_puzzles, get_following_rated, create_feed
from project.utils.user_utils import add_user

class PuzzleUtilCase(unittest.TestCase):
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
        db.session.commit()
        pass
    
    def test_pack_puzzle(self):
        user = User.query.first()
        puzzle = add_puzzle("test", user, "abcdefghij")

        #correct values for new puzzle at varying levels of detail specified
        self.assertDictContainsSubset({
            "title": 'test',
            "creator": user.name,
            "creatorID": user.id,
            "average_rating": 0,
            "play_count": 0,
            "highscore": 0
        }, pack_puzzle(puzzle, detail=1))

        self.assertDictContainsSubset({
            "scores": [],
            "average_score": 0,
            "rating_count": 0
        }, pack_puzzle(puzzle, detail=2))

        self.assertDictContainsSubset({
            "content": "abcdefghij"
        }, pack_puzzle(puzzle, detail=3))
    
    def test_add_puzzle(self):
        user = User.query.first()
        puzzle = add_puzzle("test", user, "abcdefghij")

        #verify addition to database with correct info
        self.assertIsNotNone(db.session.query(Puzzle).filter_by(id=puzzle.id).first())
        self.assertIsNotNone(db.session.query(Puzzle).filter_by(title="test",creatorID=user.id,content="abcdefghij").first())
        self.assertIsNone(db.session.query(Puzzle).filter_by(title='DoesNotExist',creatorID=user.id,content="abcdefghij").first())
    
    def test_get_puzzle(self):
        user = User.query.first()
        puzzle = add_puzzle("test", user, "abcdefghij")

        #verify correct retrieval from database with correct info
        self.assertEqual(get_puzzle("test").id, puzzle.id)
        self.assertEqual(get_puzzle(id=puzzle.id).title, "test")
        self.assertIsNone(get_puzzle(title="_test_"))
        self.assertIsNone(get_puzzle(id=-1))
    
    def test_search_puzzles(self):
        user = User.query.first()
        puzzle = add_puzzle("test", user, "abcdefghij")

        #test a puzzle can be retrieved given filters
        result = search_puzzles(query=".*tes.*", rating=[0,5], date=['0000-01-01', '9999-12-31'], completed=None, play_count=[0,99999], following=False, sort_by="date", order="desc").first()
        self.assertEqual(puzzle.id, result.id)
        result = search_puzzles(query=".*tes.*", rating=[0,1], date=['0000-01-01', '9999-12-31'], completed=None, play_count=[0,99999], following=False, sort_by="date", order="desc").first()
        self.assertEqual(puzzle.id, result.id)
        result = search_puzzles(query=".*tes.*", rating=[0,5], date=['2024-01-01', '2025-12-31'], completed=None, play_count=[0,99999], following=False, sort_by="date", order="desc").first()
        self.assertEqual(puzzle.id, result.id)
        result = search_puzzles(query=".*tes.*", rating=[0,5], date=['0000-01-01', '9999-12-31'], completed=None, play_count=[0,0], following=False, sort_by="date", order="desc").first()
        self.assertEqual(puzzle.id, result.id)

    def test_search_puzzles_query(self):
        user = add_user("user1", "password1")
        puzzle1 = add_puzzle("First Puzzle", user, "abcdefghij")
        puzzle2 = add_puzzle("Second Puzzle", user, "abcdefghij")
        puzzle3 = add_puzzle("Another Puzzle", user, "abcdefghij")
        db.session.commit()

        result = search_puzzles(query="First").all()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].title, "First Puzzle")

        result = search_puzzles(query="Puzzle$").all()
        self.assertEqual(len(result), 3)

    def test_search_puzzles_rating(self):
        user = add_user("user1", "password1")
        puzzle1 = add_puzzle("Puzzle 1", user, "abcdefghij")
        puzzle2 = add_puzzle("Puzzle 2", user, "abcdefghij")
        puzzle3 = add_puzzle("Puzzle 3", user, "abcdefghij")
        db.session.commit()

        puzzle1.add_rating(user, 4)
        puzzle2.add_rating(user, 5)
        puzzle3.add_rating(user, 3)
        db.session.commit()

        result = search_puzzles(query='^[^\$]*$',rating=(4, 5)).all()
        self.assertEqual(len(result), 2)
        self.assertIn(result[0].title, ["Puzzle 1", "Puzzle 2"])
        self.assertIn(result[1].title, ["Puzzle 1", "Puzzle 2"])

    def test_search_puzzles_date(self):
        user = add_user("user1", "password1")
        puzzle1 = add_puzzle("Puzzle 1", user, "abcdefghij")
        puzzle2 = add_puzzle("Puzzle 2", user, "abcdefghij")
        puzzle3 = add_puzzle("Puzzle 3", user, "abcdefghij")

        puzzle1.dateCreated = datetime.datetime.now() - datetime.timedelta(days=10)
        puzzle2.dateCreated = datetime.datetime.now() - datetime.timedelta(days=5)
        puzzle3.dateCreated = datetime.datetime.now() - datetime.timedelta(days=1)
        db.session.commit()

        result = search_puzzles(query='^[^\$]*$',date=((datetime.datetime.now() - datetime.timedelta(days=6)).strftime('%Y-%m-%d'), datetime.datetime.now().strftime('%Y-%m-%d'))).all()
        self.assertEqual(len(result), 2)
        self.assertIn(result[0].title, ["Puzzle 2", "Puzzle 3"])
        self.assertIn(result[1].title, ["Puzzle 2", "Puzzle 3"])

    def test_search_puzzles_completed(self):
        user = add_user("user1", "password1")
        puzzle1 = add_puzzle("Puzzle 1", user, "abcdefghij")
        puzzle2 = add_puzzle("Puzzle 2", user, "abcdefghij")
        db.session.commit()

        puzzle1.add_record(user, 10)
        db.session.commit()

        result = search_puzzles(query='^[^\$]*$',completed=(user, True)).all()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].title, "Puzzle 1")

        result = search_puzzles(query='^[^\$]*$',completed=(user, False)).all()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].title, "Puzzle 2")

    def test_search_puzzles_play_count(self):
        user = add_user("user1", "password1")
        puzzle1 = add_puzzle("Puzzle 1", user, "abcdefghij")
        puzzle2 = add_puzzle("Puzzle 2", user, "abcdefghij")
        puzzle3 = add_puzzle("Puzzle 3", user, "abcdefghij")

        puzzle1.play_count = 100
        puzzle2.play_count = 50
        puzzle3.play_count = 75
        db.session.commit()

        result = search_puzzles(query='^[^\$]*$',play_count=(50, 100)).all()
        self.assertEqual(len(result), 3)

        result = search_puzzles(query='^[^\$]*$',play_count=(50, 75)).all()
        self.assertEqual(len(result), 2)
        self.assertIn(result[0].title, ["Puzzle 2", "Puzzle 3"])
        self.assertIn(result[1].title, ["Puzzle 2", "Puzzle 3"])

    def test_search_puzzles_following(self):
        user1 = add_user("user1", "password1")
        user2 = add_user("user2", "password2")
        user3 = add_user("user3", "password3")

        user1.follow_user(user2)
        db.session.commit()

        puzzle1 = add_puzzle("Puzzle 1", user2, "abcdefghij")
        puzzle2 = add_puzzle("Puzzle 2", user3, "abcdefghij")
        db.session.commit()

        result = search_puzzles(query='^[^\$]*$',following=(user1, True)).all()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].title, "Puzzle 1")

    def test_search_puzzles_sorting(self):
        user = add_user("user1", "password1")
        puzzle1 = add_puzzle("Puzzle 1", user, "abcdefghij")
        puzzle2 = add_puzzle("Puzzle 2", user, "abcdefghij")
        puzzle3 = add_puzzle("Puzzle 3", user, "abcdefghij")

        puzzle1.play_count = 100
        puzzle2.play_count = 50
        puzzle3.play_count = 75

        puzzle1.add_record(user, 1000)
        puzzle2.add_record(user, 500)
        puzzle3.add_record(user, 750)

        puzzle1.add_rating(user, 5)
        puzzle2.add_rating(user, 4)
        puzzle3.add_rating(user, 3)
        db.session.commit()

        result = search_puzzles(query='^[^\$]*$',sort_by='play_count', order='asc').all()
        self.assertEqual(result[0].title, "Puzzle 2")
        self.assertEqual(result[1].title, "Puzzle 3")
        self.assertEqual(result[2].title, "Puzzle 1")

        result = search_puzzles(query='^[^\$]*$',sort_by='rating', order='desc').all()
        self.assertEqual(result[0].title, "Puzzle 1")
        self.assertEqual(result[1].title, "Puzzle 2")
        self.assertEqual(result[2].title, "Puzzle 3")

        result = search_puzzles(query='^[^\$]*$',sort_by='highscore', order='asc').all()
        self.assertEqual(result[0].title, "Puzzle 2")
        self.assertEqual(result[1].title, "Puzzle 3")
        self.assertEqual(result[2].title, "Puzzle 1")
    
    def test_get_following_rated(self):
        #Create users
        user1 = add_user("user1", "password1")
        user2 = add_user("user2", "password2")
        user3 = add_user("user3", "password3")

        #user1 follows user2 and user3
        user1.follow_user(user2)
        user1.follow_user(user3)

        #create puzzles
        puzzle1 = add_puzzle("Puzzle 1", user2, "abcdefghij")
        puzzle2 = add_puzzle("Puzzle 2", user3, "abcdefghij")

        #adjust creation dates for ordering tests
        puzzle1.dateCreated = datetime.datetime.now() - datetime.timedelta(days=4)
        puzzle2.dateCreated = datetime.datetime.now() - datetime.timedelta(days=3)
        db.session.commit()

        #create ratings for puzzles
        puzzle1.add_rating(user2, 5)
        puzzle2.add_rating(user3, 4)

        result = get_following_rated(user1)

        #tests
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0][0][0].title, "Puzzle 2")
        self.assertEqual(result[1][0][0].title, "Puzzle 1")
        self.assertEqual(result[0][1], "rated")
        self.assertEqual(result[1][1], "rated")

    def test_get_following_puzzles(self):
        #Create users
        user1 = add_user("user1", "password1")
        user2 = add_user("user2", "password2")
        user3 = add_user("user3", "password3")

        #user1 follows user2 and user3
        user1.follow_user(user2)
        user1.follow_user(user3)

        #create puzzles
        puzzle3 = add_puzzle("Puzzle 3", user2, "abcdefghij")
        puzzle4 = add_puzzle("Puzzle 4", user3, "abcdefghij")

        #adjust creation dates for ordering tests
        puzzle3.dateCreated = datetime.datetime.now() - datetime.timedelta(days=2)
        puzzle4.dateCreated = datetime.datetime.now() - datetime.timedelta(days=1)
        db.session.commit()

        result = get_following_puzzles(user1)

        #tests
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0][0].title, "Puzzle 4")
        self.assertEqual(result[1][0].title, "Puzzle 3")
        self.assertEqual(result[0][1], "created")
        self.assertEqual(result[1][1], "created")

    def test_create_feed(self):
        #Create users
        user1 = add_user("user1", "password1")
        user2 = add_user("user2", "password2")
        user3 = add_user("user3", "password3")

        #user1 follows user2 and user3
        user1.follow_user(user2)
        user1.follow_user(user3)

        #create puzzles
        puzzle1 = add_puzzle("Puzzle 1", user2, "abcdefghij")
        puzzle2 = add_puzzle("Puzzle 2", user3, "abcdefghij")
        puzzle3 = add_puzzle("Puzzle 3", user2, "abcdefghij")
        puzzle4 = add_puzzle("Puzzle 4", user3, "abcdefghij")

        #adjust creation dates for ordering tests
        puzzle1.dateCreated = datetime.datetime.now() - datetime.timedelta(days=4)
        puzzle2.dateCreated = datetime.datetime.now() - datetime.timedelta(days=3)
        puzzle3.dateCreated = datetime.datetime.now() - datetime.timedelta(days=2)
        puzzle4.dateCreated = datetime.datetime.now() - datetime.timedelta(days=1)
        db.session.commit()

        #create ratings for puzzles
        puzzle1.add_rating(user2, 5)
        puzzle2.add_rating(user3, 4)

        result = create_feed(user1)

        #tests
        self.assertEqual(len(result), 6)
        self.assertEqual(result[0][0].title, "Puzzle 2")
        self.assertEqual(result[1][0].title, "Puzzle 1")
        self.assertEqual(result[2][0].title, "Puzzle 4")
        self.assertEqual(result[3][0].title, "Puzzle 3")
        self.assertEqual(result[4][0].title, "Puzzle 2")
        self.assertEqual(result[5][0].title, "Puzzle 1")