import unittest

from sqlalchemy import exc

from tests import TestObject, app

from project.blueprints.models import db, User, Follow

from project.utils import user_utils

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
    
    def test_password(self):
        '''
        Tests that only identical passwords result in a pass
        '''
        current_user = user_utils.add_user("MAIN_USER", "132131")
        current_user.set_password("hello")

        self.assertTrue(current_user.check_password("hello"))
        self.assertFalse(current_user.check_password("Hello"))
        self.assertFalse(current_user.check_password("bye"))
        self.assertFalse(current_user.check_password(""))

    def test_name_unique(self):
        '''
        Tests that only distinct usernames can exist in the User table
        '''
        user_utils.add_user("MAIN_USER", "132131")
        self.assertRaises(exc.IntegrityError, user_utils.add_user, "MAIN_USER", "789")
        db.session.rollback()

    def test_follow(self):
        '''
        Tests that the relationship between User and Follow ORMs is correct and appends followers correctly.
        \nTests the is_following method of User
        '''
        current_user = user_utils.add_user("MAIN_USER", "132131")
        
        for i in range(5):
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
        self.assertRaises(exc.IntegrityError, u2.follow_user, current_user)
        db.session.rollback()
        self.assertTrue(u2.unfollow_user(current_user))
        self.assertFalse(u2.unfollow_user(current_user))
        self.assertFalse(u2.is_following(current_user))
        self.assertIsNone(db.session.query(Follow).filter_by(userID=current_user.id, followerID=u2.id).first())