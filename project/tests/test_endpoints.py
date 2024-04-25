import unittest, json

from sqlalchemy import exc

from flask import url_for

from project.tests import TestObject

from project import app
from project.blueprints.models import db, User, Follow, Puzzle, LeaderboardRecord, Rating

from project.utils import user_utils, puzzle_utils, route_utils as route

class GetRequestCase(unittest.TestCase):
    def setUp(self):
        self.app_context = app.test_request_context()
        self.app_context.push()
        self.client = app.test_client()
        self.t = TestObject(app, db)
        self.t.add_test_client(self.client)
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_pages_load(self):
        expected = {
            route.index: 200,
            route.login: 200,
            route.register: 200,
            route.profile: 302,
            route.logout: 302,
            route.wordGame: 200,
            route.solve: 405,
            route.getuser: 200
        }
        for path, code in expected.items():
            response = self.client.get(url_for(path))
            self.assertEqual(response.status_code, code)

        user = user_utils.add_user("GET_USER", "123")
        response = self.t.login("GET_USER", "123")
        self.assertEqual(response.status_code, 200)
        response = self.client.get(url_for(route.profile))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(url_for(route.getuser))
        data = json.loads(response.data)
        self.assertIsNotNone(data)
        self.assertEqual(data['id'], user.id)
        self.assertEqual(data['username'], user.name)
        response = self.client.get(url_for(route.logout))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(url_for(route.getuser))
        self.assertEqual(json.loads(response.data)['id'], -1)
    
    def test_get_puzzle(self):
        pass

    def test_search_puzzles(self):
        pass

    def test_get_user_info(self):
        pass

class PostRequestCase(unittest.TestCase):
    def setUp(self):
        self.app_context = app.test_request_context()
        self.app_context.push()
        self.client = app.test_client()
        self.t = TestObject(app, db)
        self.t.add_test_client(self.client)
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_account(self):
        response = self.t.register("POST_USER", "123")
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(user_utils.get_user("POST_USER"))
        self.assertEqual(url_for(route.register), response.request.path)

        response = self.t.register("POST_USER", "Valid123456")
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(user_utils.get_user("POST_USER"))
        self.assertEqual(url_for(route.login), response.request.path)

        response = self.t.register("POST_USER", "AnotherValidPassword")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(url_for(route.register), response.request.path)
    
    def test_login_account(self):
        self.t.register("POST_USER", "Valid123456")

        response = self.t.login("INVALID_POST_USER", "Valid123456")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(url_for(route.login), response.request.path)

        response = self.t.login("POST_USER", "Invalid")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(url_for(route.login), response.request.path)

        response = self.t.login("POST_USER", "Valid123456")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(url_for(route.profile), response.request.path)
    
    def test_create_puzzle(self):
        pass
    
    def test_follow(self):
        pass

    def test_rate(self):
        pass

    def test_submit_score(self):
        pass
        

if __name__ == '__main__':
    unittest.main(verbosity=2)
    
