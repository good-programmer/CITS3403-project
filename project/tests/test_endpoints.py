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

    def test_search_puzzles(self):
        pass

    def test_get_user_info(self):
        user = user_utils.add_user("GET_USER", "123")
        response = self.client.get(url_for(route.user.get, userid=user.id))
        data = json.loads(response.data)
        self.assertIsNotNone(data)
        self.assertEqual(data['id'], user.id)
        self.assertEqual(data['username'], user.name)
    
    def test_get_user_follows(self):
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
    def setUp(self):
        self.app_context = app.test_request_context()
        self.app_context.push()
        self.client = app.test_client()
        self.t = TestObject(app, db)
        self.t.add_test_client(self.client)
        db.create_all()

    def tearDown(self):
        self.t.logout()
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
        response = self.client.post(url_for(route.puzzle.create), data=dict(puzzlename="ENDPOINT_TEST_PUZZLE_ERROR", puzzle="ABCDEFGHI"), follow_redirects=True)
        self.assertEqual(response.status_code, 401)
        response = self.client.post(url_for(route.puzzle.create), data=dict(puzzlename="ENDPOINT_TEST_PUZZLE_ERROR", puzzle="ALKJLKLKJLKLKJLKJBCDEFGHI"), follow_redirects=True)
        self.assertEqual(url_for(route.puzzle.create), response.request.path)

        self.t.register("POST_USER", "Valid123456")
        response = self.t.login("POST_USER", "Valid123456")
        response = self.client.post(url_for(route.puzzle.create), data=dict(puzzlename="ENDPOINT_TEST_PUZZLE", puzzle="ABCDEFGHI"), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(url_for(route.index), response.request.path)
        self.assertIsNotNone(puzzle_utils.get_puzzle("ENDPOINT_TEST_PUZZLE"))
    
    def test_follow(self):
        user1 = user_utils.add_user("POST_USER1", "123")
        user2 = user_utils.add_user("POST_USER2", "123")
        
        response = self.client.post(url_for(route.user.follow), data=dict(id=user2.id), follow_redirects=True)
        self.assertEqual(response.status_code, 401)
        response = self.client.post(url_for(route.user.unfollow), data=dict(id=user2.id), follow_redirects=True)
        self.assertEqual(response.status_code, 401)

        self.t.login("POST_USER1","123")
        response = self.client.post(url_for(route.user.follow), data=dict(id=user2.id), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(user1.is_following(user2))
        self.assertTrue(user1.id in [u.followerID for u in user2.followers])
        response = self.client.post(url_for(route.user.unfollow), data=dict(id=user2.id), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(user1.is_following(user2))
        self.assertFalse(user1.id in [u.followerID for u in user2.followers])

    def test_rate(self):
        pass

    def test_submit_score(self):
        pass
        

if __name__ == '__main__':
    unittest.main(verbosity=2)
    
