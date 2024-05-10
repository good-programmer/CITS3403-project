'''
Tests user-related endpoints
'''
import unittest, json

from flask import url_for

from tests import TestObject, app

from project.blueprints.models import db

from project.utils import user_utils, puzzle_utils, route_utils as route

class GetRequestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app_context = app.test_request_context()
        cls.app_context.push()
        cls.client = app.test_client()
        cls.t = TestObject(app, db)
        cls.t.add_test_client(cls.client)   
        return super().setUpClass()

    def tearDown(self):
        self.t.logout()
        self.t.clear_db()
    
    @classmethod
    def tearDownClass(cls) -> None:
        cls.t.clear_db()
        cls.app_context.pop()
        return super().tearDownClass()
    
    def assertCode(self, response, code):
        '''Check HTTP request code is expected'''
        assert response.status_code == code, f'Expected status code {code}, got {response.status_code} for {response.request.path}'
        return response
    
    def test_get_user_info(self):
        '''
        Tests that a user's name can be retrieved by their id.
        '''
        user = user_utils.add_user("GET_USER", "123")
        response = self.client.get(url_for(route.user.get, userid=user.id))
        data = json.loads(response.data)
        self.assertIsNotNone(data)
        self.assertEqual(data['id'], user.id)
        self.assertEqual(data['username'], user.name)
    
    def test_get_user_follows(self):
        '''
        Tests that a user's followers and their follows can be retreived by their id.
        '''
        user = user_utils.add_user("GET_USER", "123")
        f1 = user_utils.add_user("GET_FOLLOWER1", "123")
        f2 = user_utils.add_user("GET_FOLLOWER2", "123")
        f3 = user_utils.add_user("GET_FOLLOWER3", "123")
        f1.follow_user(user)
        f2.follow_user(user)
        f3.follow_user(user)
        user.follow_user(f1)
        user.follow_user(f2)
        user.follow_user(f3)

        response = self.client.get(url_for(route.user.get, userid=user.id))
        data = json.loads(response.data)
        self.assertIsNotNone(data)
        self.assertListEqual(data['followers'], [{"id": u.followerID, "name": u.follower.name} for u in user.followers])
        self.assertListEqual(data['following'], [{"id": u.userID, "name": u.user.name} for u in user.following])
    
    def test_get_user_scores(self):
        '''
        Tests that a given user's scores can be retrieved by their id, and that given a puzzle, their score for that puzzle can also be retrieved.
        '''
        user = user_utils.add_user("GET_USER1", "123")
        puzzle1 = puzzle_utils.add_puzzle("GET_PUZZLE1", user, "ABCEFGHJI")
        puzzle2 = puzzle_utils.add_puzzle("GET_PUZZLE2", user, "ABCEFGHJI")
        puzzle1.add_record(user, 30)
        puzzle2.add_record(user, 20)
        response = self.client.get(url_for(route.user.get, userid=user.id))
        data = json.loads(response.data)
        self.assertIsNotNone(data)
        self.assertListEqual(data['scores'], [{"id": s.puzzleID, "title": s.puzzle.title, "creator": s.puzzle.creator.name, "creatorID": s.puzzle.creatorID, "play_count": s.puzzle.play_count, "score": s.score, "dateSubmitted": str(s.dateSubmitted)} for s in user.scores])
        self.t.login("GET_USER1", "123")
        response = self.client.get(url_for(route.puzzle.get, puzzleid=puzzle1.id))
        data = json.loads(response.data)
        self.assertIsNotNone(data)
        self.assertIsNotNone(data['score'])
        self.assertEqual(data['score']['score'], 30)

    def test_get_user_ratings(self):
        '''
        Tests that a given user's ratings can be retrieved by their id, and that given a puzzle, their rating for that puzzle can also be retrieved.
        '''
        user = user_utils.add_user("GET_USER1", "123")
        puzzle1 = puzzle_utils.add_puzzle("GET_PUZZLE1", user, "ABCEFGHJI")
        puzzle2 = puzzle_utils.add_puzzle("GET_PUZZLE2", user, "ABCEFGHJI")
        puzzle1.add_rating(user, 3)
        puzzle2.add_rating(user, 2)
        response = self.client.get(url_for(route.user.get, userid=user.id))
        data = json.loads(response.data)
        self.assertIsNotNone(data)
        self.assertListEqual(data['ratings'], [{"id": r.puzzleID, "title": r.puzzle.title, "creator": r.puzzle.creator.name, "creatorID": r.puzzle.creatorID, "play_count": r.puzzle.play_count, "rating": r.rating, "dateRated": str(r.dateRated)} for r in user.ratings])
        self.t.login("GET_USER1", "123")
        response = self.client.get(url_for(route.puzzle.get, puzzleid=puzzle1.id))
        data = json.loads(response.data)
        self.assertIsNotNone(data)
        self.assertIsNotNone(data['rated'])
        self.assertEqual(data['rated']['rating'], 3)

class PostRequestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app_context = app.test_request_context()
        cls.app_context.push()
        cls.client = app.test_client()
        cls.t = TestObject(app, db)
        cls.t.add_test_client(cls.client)
        return super().setUpClass()

    def tearDown(self):
        self.t.logout()
        self.t.clear_db()
    
    @classmethod
    def tearDownClass(cls) -> None:
        cls.app_context.pop()
        return super().tearDownClass()
    
    def assertCode(self, request, code):
        '''Check HTTP request code is expected'''
        assert request.status_code == code, f'Expected status code {code}, got {request.status_code}'
        return request
    
    def test_create_account(self):
        '''
        Tests the account registration endpoint. 
        \nTests that an invalid credentials or a taken username correctly redirects back to the registration page.
        \nTests that valid credentials and successful registration correctly redirects to login page.
        '''
        #invalid password
        response = self.assertCode(self.t.register("POST_USER", "123"), 200)
        self.assertIsNone(user_utils.get_user("POST_USER"))
        self.assertEqual(url_for(route.register), response.request.path)

        #successful register
        response = self.assertCode(self.t.register("POST_USER", "Valid123456"), 200)
        self.assertIsNotNone(user_utils.get_user("POST_USER"))
        self.assertEqual(url_for(route.login), response.request.path)

        #taken username
        response = self.assertCode(self.t.register("POST_USER", "AnotherValidPassword"), 200)
        self.assertEqual(url_for(route.register), response.request.path)
    
    def test_login_account(self):
        '''
        Tests that invalid login credentials redirects to login page.
        \nTests that valid login credentials redirects to profile page.
        '''
        self.t.register("POST_USER", "Valid123456")

        def assertInvalidLogin(username, password):
            response = self.assertCode(self.t.login(username, password), 200)
            self.assertEqual(url_for(route.login), response.request.path)
        #invalid username
        assertInvalidLogin("INVALID_POST_USER", "Valid123456")
        assertInvalidLogin("", "Valid123456")
        #invalid password
        assertInvalidLogin("POST_USER", "Invalid")
        assertInvalidLogin("POST_USER", "")
        #invalid both
        assertInvalidLogin("INVALID_POST_USER", "Invalid")
        assertInvalidLogin("", "")

        #correct credentials
        response = self.assertCode(self.t.login("POST_USER", "Valid123456"), 200)
        self.assertEqual(url_for(route.user.profile, userid=user_utils.get_user(name="POST_USER").id), response.request.path)

    def test_follow(self):
        '''
        Tests the follow and unfollow endpoints.
        \nTests that an unauthenticated user cannot follow or unfollow a user.
        \nTests that an authenticated user can follow and unfollow another user.
        \nTests that an appropriate error is returned if a user attempts to (un)follow a user they are (not) following.
        '''
        user1 = user_utils.add_user("POST_USER1", "123")
        user2 = user_utils.add_user("POST_USER2", "123")
        data = dict(id=user2.id)
        
        #unauthenticated case
        self.assertCode(self.client.post(url_for(route.user.follow), json=data, follow_redirects=True), 401)
        self.assertCode(self.client.post(url_for(route.user.unfollow), json=data, follow_redirects=True), 401)
        #valid cases
        self.t.login("POST_USER1","123")
        self.assertCode(self.client.post(url_for(route.user.follow), json=data, follow_redirects=True), 200)
        self.assertTrue(user1.is_following(user2))
        self.assertTrue(user1.id in [u.followerID for u in user2.followers])
        #error case (follow)
        self.assertCode(self.client.post(url_for(route.user.follow), json=data, follow_redirects=True), 400)
        self.assertCode(self.client.post(url_for(route.user.unfollow), json=data, follow_redirects=True), 200)
        self.assertFalse(user1.is_following(user2))
        self.assertFalse(user1.id in [u.followerID for u in user2.followers])
        #error case (unfollow)
        self.assertCode(self.client.post(url_for(route.user.unfollow), json=data, follow_redirects=True), 400)