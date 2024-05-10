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

from project.utils.puzzle_utils import pack_puzzle, add_puzzle, get_puzzle, search_puzzles

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
        Puzzle.query.filter_by(title="test").delete()
        db.session.commit()
        pass
    
    def test_pack_puzzle(self):
        user = User.query.first()
        puzzle = add_puzzle("test", user, "abcdefghij")

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
        self.assertIsNotNone(db.session.query(Puzzle).filter_by(id=puzzle.id).first())
        self.assertIsNotNone(db.session.query(Puzzle).filter_by(title="test",creatorID=user.id,content="abcdefghij").first())
        self.assertIsNone(db.session.query(Puzzle).filter_by(title='DoesNotExist',creatorID=user.id,content="abcdefghij").first())
    
    def test_get_puzzle(self):
        user = User.query.first()
        puzzle = add_puzzle("test", user, "abcdefghij")

        self.assertEqual(get_puzzle("test").id, puzzle.id)
        self.assertEqual(get_puzzle(id=puzzle.id).title, "test")
        self.assertIsNone(get_puzzle(title="_test_"))
        self.assertIsNone(get_puzzle(id=-1))
    
    def test_search_puzzles(self):
        user = User.query.first()
        puzzle = add_puzzle("test", user, "abcdefghij")
        result = search_puzzles(query=".*tes.*", rating=[0,5], date=['0000-01-01', '9999-12-31'], completed=None, play_count=[0,99999], sort_by="date", order="desc").first()
        self.assertEqual(puzzle.id, result.id)
        
    

