import unittest

from sqlalchemy import exc

from tests import app, TestObject

from project.blueprints.models import db, User

from project.utils.user_utils import pack_user, verify_user, add_user, get_user

class UserUtilCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app_context = app.app_context()
        cls.app_context.push()
        cls.t = TestObject(app, db)

        return super().setUpClass()
    
    def setUp(self):
        pass

    def tearDown(self):
        User.query.filter_by(name="test").delete()
        db.session.commit()
        pass

    def test_pack_user(self):
        user = add_user("test", "*****")

        #tests default values are correct
        self.assertDictContainsSubset({
            "username": 'test',
            "followers": [],
            "following": [],
            "scores": [],
            "ratings": [],
            "puzzles": [],
            "highscore": None
        }, pack_user(user))
    
    def test_add_user(self):
        user = add_user("test", "*****")

        #verify addition to database with correct info
        self.assertIsNotNone(db.session.query(User).filter_by(id=user.id).first())
        self.assertIsNotNone(db.session.query(User).filter_by(name="test",id=user.id).first())
        self.assertIsNone(db.session.query(User).filter_by(name='DoesNotExist').first())
    
    def test_get_user(self):
        user = add_user("test", "*****")

        #verify correct retrieval from database with correct info
        self.assertEqual(get_user("test").id, user.id)
        self.assertEqual(get_user(id=user.id).name, "test")
        self.assertIsNone(get_user(name="_test_"))
        self.assertIsNone(get_user(id=-1))
    
    def test_verify_user(self):
        user = add_user("test", "*****")

        #valid
        self.assertIsNotNone(verify_user("test"))
        self.assertIsNotNone(verify_user("test","*****"))
        #invalid
        self.assertIsNone(verify_user("_test_"))                     
        self.assertIsNone(verify_user("test",""))
        self.assertIsNone(verify_user("test", "abc"))