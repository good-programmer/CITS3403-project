import os
import sys
topdir = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(topdir)

os.environ['DATABASE_URL'] = f"sqlite:///{os.path.dirname(os.path.abspath(__file__))}/db/test.db"
print(os.environ['DATABASE_URL'])

from datetime import datetime, timezone, timedelta
import unittest

from project import app
from project.blueprints.models import db, User, Follow

from project.utils import user_utils

class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_follow(self):
        current_user = User(name="MAIN_USER", password="132131")
        db.session.add(current_user)
        db.session.commit()
        
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

if __name__ == '__main__':
    unittest.main(verbosity=2)