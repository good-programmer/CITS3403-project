import unittest, json

from sqlalchemy import exc, MetaData

from flask import url_for

from project.tests import TestObject

from project import app
from project.blueprints.models import db, User, Follow, Puzzle, LeaderboardRecord, Rating

from project.utils import user_utils, puzzle_utils, route_utils as route

import datetime

class GetRequestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app_context = app.test_request_context()
        cls.app_context.push()
        db.create_all()
        cls.client = app.test_client()
        cls.t = TestObject(app, db)
        cls.t.add_test_client(cls.client)
        return super().setUpClass()

    def tearDown(self):
        self.t.logout()
        self.t.clear_db()
    
    @classmethod
    def tearDownClass(cls) -> None:
        cls.t.clear_db(True)
        cls.app_context.pop()
        return super().tearDownClass()
    
    def test_pages_load(self):
        '''
        Test that a user can visit the expected web pages. Includes cases for authenticated-only pages as well.
        '''
        expected = {
            route.index: 200,
            route.login: 200,
            route.register: 200,
            route.profile: 302,
            route.logout: 302,
            route.wordGame: 200,
            route.solve: 405,
            route.user.current: 200
        }
        for path, code in expected.items():
            response = self.client.get(url_for(path))
            self.assertEqual(response.status_code, code)

        user = user_utils.add_user("GET_USER", "123")
        response = self.t.login("GET_USER", "123")
        self.assertEqual(response.status_code, 200)
        response = self.client.get(url_for(route.profile))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(url_for(route.user.current))
        data = json.loads(response.data)
        self.assertIsNotNone(data)
        self.assertEqual(data['id'], user.id)
        self.assertEqual(data['username'], user.name)
        response = self.client.get(url_for(route.logout))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(url_for(route.user.current))
        self.assertEqual(json.loads(response.data)['id'], -1)
    
    def test_get_puzzle(self):
        '''
        Tests that a puzzle's information can be retrieved by id using the appropriate GET endpoint.
        '''
        user = user_utils.add_user("GET_USER", "123")
        puzzle = puzzle_utils.add_puzzle(title="ENDPOINT_TEST_PUZZLE", creator=user, content="ABCDEFGHI")
        response = self.client.get(url_for(route.puzzle.get, puzzleid=puzzle.id))
        data = json.loads(response.data)
        self.assertIsNotNone(data)
        self.assertEqual(data['id'], puzzle.id)
        self.assertEqual(data['title'], puzzle.title)
        self.assertEqual(data['content'], puzzle.content)
        self.assertEqual(data['dateCreated'], puzzle.dateCreated.ctime())
        self.assertEqual(data['creatorID'], puzzle.creatorID)
        self.assertEqual(data['average_rating'], puzzle.average_rating)
        self.assertEqual(data['average_score'], puzzle.average_score)
        response = self.client.get(url_for(route.puzzle.get, puzzleid=-1))
        self.assertEqual(response.status_code, 404)

    def test_puzzle_trends(self):
        '''
        Tests that a list of puzzles (and their information) can be retrieved by some common trends.
        \npuzzles/recent
        \npuzzles/hot (most popular within X period of time)
        \npuzzles/popular (most popular overall)
        '''
        #from database
        recent = Puzzle.query.order_by(db.desc(Puzzle.dateCreated)).limit(10).all()
        recent = [{
            "id": p.id,
            "title": p.title,
            "creatorID": p.creatorID,
            "creator": p.creator.name,
            "play_count": p.play_count,
            "average_rating": p.average_rating
        } for p in recent]

        t = datetime.datetime.now() - datetime.timedelta(weeks=1)
        hot = Puzzle.query.where(Puzzle.dateCreated > t).order_by(db.desc(Puzzle.play_count)).limit(10).all()
        hot = [{
            "id": p.id,
            "title": p.title,
            "creatorID": p.creatorID,
            "creator": p.creator.name,
            "play_count": p.play_count,
            "average_rating": p.average_rating
        } for p in hot]

        popular = Puzzle.query.order_by(db.desc(Puzzle.play_count)).limit(10).all()
        popular = [{
            "id": p.id,
            "title": p.title,
            "creatorID": p.creatorID,
            "creator": p.creator.name,
            "play_count": p.play_count,
            "average_rating": p.average_rating
        } for p in popular]

        #recent case
        response = self.client.get(url_for(route.puzzle.recent, page=1))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertListEqual(data, recent)

        #hot case
        response = self.client.get(url_for(route.puzzle.hot, page=1))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertListEqual(data, hot)

        #popular case
        response = self.client.get(url_for(route.puzzle.popular, page=1))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertListEqual(data, popular)
    
    def test_puzzle_search(self):
        '''Tests that a list of puzzles (and their information) can be retrieved given a list of queries, filters, and sorts'''
        pass

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
        self.assertListEqual(data['scores'], [{"puzzleID": s.puzzleID, "puzzle": s.puzzle.title, "score": s.score, "dateSubmitted": s.dateSubmitted.ctime()} for s in user.scores])
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
        self.assertListEqual(data['ratings'], [{"puzzleID": r.puzzleID, "puzzle": r.puzzle.title, "rating": r.rating, "dateRated": r.dateRated.ctime()} for r in user.ratings])
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
        db.create_all()
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

    def test_create_account(self):
        '''
        Tests the account registration endpoint. 
        \nTests that an invalid credentials or a taken username correctly redirects back to the registration page.
        \nTests that valid credentials and successful registration correctly redirects to login page.
        '''
        #invalid password
        response = self.t.register("POST_USER", "123")
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(user_utils.get_user("POST_USER"))
        self.assertEqual(url_for(route.register), response.request.path)

        #successful register
        response = self.t.register("POST_USER", "Valid123456")
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(user_utils.get_user("POST_USER"))
        self.assertEqual(url_for(route.login), response.request.path)

        #taken username
        response = self.t.register("POST_USER", "AnotherValidPassword")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(url_for(route.register), response.request.path)
    
    def test_login_account(self):
        '''
        Tests that invalid login credentials redirects to login page.
        \nTests that valid login credentials redirects to profile page.
        '''
        self.t.register("POST_USER", "Valid123456")

        #invalid username
        response = self.t.login("INVALID_POST_USER", "Valid123456")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(url_for(route.login), response.request.path)

        #invalid password
        response = self.t.login("POST_USER", "Invalid")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(url_for(route.login), response.request.path)

        #correct credentials
        response = self.t.login("POST_USER", "Valid123456")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(url_for(route.profile), response.request.path)
    
    def test_create_puzzle(self):
        '''
        Tests the puzzle creation endpoint.
        \nTests that an unauthenticated user cannot create a puzzle.
        \nTests that an authenticated user can create a puzzle, that the status code is correct, and that they are redirected correctly.
        '''
        #unauthenticated case
        response = self.client.post(url_for(route.puzzle.create), data=dict(puzzlename="ENDPOINT_TEST_PUZZLE_ERROR", puzzle="ABCDEFGHI"), follow_redirects=True)
        self.assertEqual(response.status_code, 401)
        response = self.client.post(url_for(route.puzzle.create), data=dict(puzzlename="ENDPOINT_TEST_PUZZLE_ERROR", puzzle="ALKJLKLKJLKLKJLKJBCDEFGHI"), follow_redirects=True)
        self.assertEqual(url_for(route.puzzle.create), response.request.path)

        #authenticated case
        self.t.register("POST_USER", "Valid123456")
        response = self.t.login("POST_USER", "Valid123456")
        response = self.client.post(url_for(route.puzzle.create), data=dict(puzzlename="ENDPOINT_TEST_PUZZLE", puzzle="ABCDEFGHI"), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(url_for(route.index), response.request.path)
        self.assertIsNotNone(puzzle_utils.get_puzzle("ENDPOINT_TEST_PUZZLE"))
    
    def test_follow(self):
        '''
        Tests the follow and unfollow endpoints.
        \nTests that an unauthenticated user cannot follow or unfollow a user.
        \nTests that an authenticated user can follow and unfollow another user.
        \nTests that an appropriate error is returned if a user attempts to (un)follow a user they are (not) following.
        '''
        user1 = user_utils.add_user("POST_USER1", "123")
        user2 = user_utils.add_user("POST_USER2", "123")
        
        #unauthenticated case
        response = self.client.post(url_for(route.user.follow), data=dict(id=user2.id), follow_redirects=True)
        self.assertEqual(response.status_code, 401)
        response = self.client.post(url_for(route.user.unfollow), data=dict(id=user2.id), follow_redirects=True)
        self.assertEqual(response.status_code, 401)

        #valid cases
        self.t.login("POST_USER1","123")
        response = self.client.post(url_for(route.user.follow), data=dict(id=user2.id), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(user1.is_following(user2))
        self.assertTrue(user1.id in [u.followerID for u in user2.followers])
        #error case (follow)
        response = self.client.post(url_for(route.user.follow), data=dict(id=user2.id), follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        response = self.client.post(url_for(route.user.unfollow), data=dict(id=user2.id), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(user1.is_following(user2))
        self.assertFalse(user1.id in [u.followerID for u in user2.followers])
        #error case (unfollow)
        response = self.client.post(url_for(route.user.unfollow), data=dict(id=user2.id), follow_redirects=True)
        self.assertEqual(response.status_code, 400)

    def test_rate(self):
        '''
        Tests the /puzzle/<puzzleid>/rate endpoint.
        \nTests a user's ability to rate a puzzle if they are logged in and have completed it (and errors if not).
        \nTests that the returned average is equal to the new average rating.
        '''
        user = user_utils.add_user("POST_USER", "123")
        __ = user_utils.add_user("__", "123")
        puzzle = puzzle_utils.add_puzzle("POST_PUZZLE", __, "ABCEFGHJI")
        puzzle.add_record(__, 30)
        puzzle.add_rating(__, 5)

        #unauthenticated case
        response = self.client.post(url_for(route.puzzle.rate, puzzleid=puzzle.id), data=dict(rating=2), follow_redirects=True)
        self.assertEqual(response.status_code, 401)
        #uncompleted case
        self.t.login("POST_USER", "123")
        response = self.client.post(url_for(route.puzzle.rate, puzzleid=puzzle.id), data=dict(rating=2), follow_redirects=True)
        self.assertEqual(response.status_code, 401)
        #correct case
        puzzle.add_record(user, 50)
        response = self.client.post(url_for(route.puzzle.rate, puzzleid=puzzle.id), data=dict(rating=2), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        #test average
        self.assertEqual(json.loads(response.data)['average_rating'], puzzle.average_rating)
        #404 (invalid puzzle) case
        response = self.client.post(url_for(route.puzzle.rate, puzzleid=-1), data=dict(rating=2), follow_redirects=True)
        self.assertEqual(response.status_code, 404)

    def test_submit_score(self):
        pass
        

if __name__ == '__main__':
    unittest.main(verbosity=2)
    
