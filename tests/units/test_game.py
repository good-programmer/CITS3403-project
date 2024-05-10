import unittest, json

from flask import url_for

from tests import TestObject, app

from project.blueprints.models import db, Puzzle

from project.utils import user_utils, puzzle_utils, route_utils as route

import datetime

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
    
    def test_pages_load(self):
        '''
        Test that a user can visit the expected web pages. Includes cases for authenticated-only pages as well.
        '''
        expected = {
            route.index: 200,
            route.login: 200,
            route.register: 200,
            route.logout: 302,
            route.user.current: 200,
            route.puzzle.create: 302
        }
        for path, code in expected.items():
            self.assertCode(self.client.get(url_for(path)), code)
        self.assertCode(self.client.get(url_for(route.puzzle.play, puzzleid=1), follow_redirects=False), 302)

        user = user_utils.add_user("GET_USER", "123")
        self.assertCode(self.t.login("GET_USER", "123"),200)
        self.assertCode(self.client.get(url_for(route.puzzle.create)), 200)
        self.assertCode(self.client.get(url_for(route.user.profile, userid=user.id)),200)
        response = self.client.get(url_for(route.user.current))
        data = json.loads(response.data)
        self.assertIsNotNone(data)
        self.assertEqual(data['id'], user.id)
        self.assertEqual(data['username'], user.name)
        self.assertCode(self.client.get(url_for(route.logout)),302)
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
        self.assertEqual(data['dateCreated'], str(puzzle.dateCreated))
        self.assertEqual(data['creatorID'], puzzle.creatorID)
        self.assertEqual(data['average_rating'], puzzle.average_rating)
        self.assertEqual(data['average_score'], puzzle.average_score)
        self.assertCode(self.client.get(url_for(route.puzzle.get, puzzleid=-1)),404)

    def test_puzzle_trends(self):
        '''
        Tests that a list of puzzles (and their information) can be retrieved by some common trends.
        \npuzzles/recent
        \npuzzles/hot (most popular within X period of time)
        \npuzzles/popular (most popular overall)
        '''
        #from database
        recent = Puzzle.query.order_by(db.desc(Puzzle.dateCreated)).limit(10).all()
        recent = [p.title for p in recent]

        t = datetime.datetime.now() - datetime.timedelta(weeks=1)
        hot = Puzzle.query.where(Puzzle.dateCreated > t).order_by(db.desc(Puzzle.play_count)).limit(10).all()
        hot = [p.title for p in hot]

        popular = Puzzle.query.order_by(db.desc(Puzzle.play_count)).limit(10).all()
        popular = [p.title for p in popular]

        #recent case
        response = self.assertCode(self.client.get(url_for(route.puzzle.search, trend='recent', page=1)),200)
        data = [i['title'] for i in json.loads(response.data)['puzzles']]
        self.assertListEqual(data, recent)

        #hot case
        response = self.assertCode(self.client.get(url_for(route.puzzle.search, trend='hot', page=1)),200)
        data = [i['title'] for i in json.loads(response.data)['puzzles']]
        self.assertListEqual(data, hot)

        #popular case
        response = self.assertCode(self.client.get(url_for(route.puzzle.search, trend='popular', page=1)),200)
        data = [i['title'] for i in json.loads(response.data)['puzzles']]
        self.assertListEqual(data, popular)

        #404 case
        self.assertCode(self.client.get(url_for(route.puzzle.search, trend='notvalid', page=1)),404)
    
    def test_puzzle_search(self):
        '''Tests that a list of puzzles (and their information) can be retrieved given a list of queries, filters, and sorts
        \n-creator name
        \n-rating
        \n-date created interval
        \n-completed/incomplete
        \n-play count
        \n-puzzle title
        '''
        def puzzle_get(**kwargs): #auxiliary function to make a GET request to /puzzle/search with parameters
            return self.client.get(url_for(route.puzzle.search, page_size=1000, page=1, **kwargs))
        
        def parse_puzzle_search_response(response): #auxiliary function to parse the GET requests
            self.assertEqual(response.status_code, 200)
            result = json.loads(response.data)
            result = [i['title'] for i in result['puzzles']]
            return result
        
        def test_search_sort(sort_by, key): #auxiliary function to test sort options
            response = puzzle_get(sort_by=sort_by, order='desc')
            expected = sorted([p for p in Puzzle.query.all()],key=key, reverse=True)
            expected = [p.title for p in expected]
            self.assertEqual(expected, parse_puzzle_search_response(response))
        
        #search by puzzle title
        query = 'g PUZZLE 2$'
        response = puzzle_get(query=query)
        expected = ['$GENERATED_PUZZLE_' + str(2 + i*10) for i in range(self.t.numPuzzles//10)]
        self.assertCountEqual(expected, parse_puzzle_search_response(response))

        #search by puzzle creator
        query = "gen use 5$"
        response = puzzle_get(query=query)
        expected = [p.title for x in range(self.t.numUsers//10) for p in user_utils.get_user(name=f'$GENERATED_USER_{5+x*10}').puzzles]
        self.assertCountEqual(expected, parse_puzzle_search_response(response))

        #search by rating
        lower, upper = 1, 2                                                                          
        response = puzzle_get(rating=f'{lower}-{upper}')
        expected = [p.title for p in Puzzle.query.all() if lower<=p.average_rating<=upper]
        self.assertCountEqual(expected, parse_puzzle_search_response(response))
        
        #search by date created
        lower, upper = '2000-01-01', '2002-01-01'                                                                     
        response = puzzle_get(after=lower, to=upper)
        expected = [p.title for p in Puzzle.query.all() if datetime.datetime.strptime(lower, '%Y-%m-%d')<=p.dateCreated<=datetime.datetime.strptime(upper, '%Y-%m-%d')]
        self.assertCountEqual(expected, parse_puzzle_search_response(response))
        
        #search by completeed
        user = self.t.get_random_user()
        self.t.login(user.name, "123")
        response = puzzle_get(completed=True)
        expected = [p.puzzle.title for p in user.scores]
        self.assertCountEqual(expected, parse_puzzle_search_response(response))

        #search by uncompleted
        response = puzzle_get(completed=False)
        r = [l.puzzleID for l in user.scores]
        expected = [p.title for p in Puzzle.query.all() if p.id not in r]
        self.assertCountEqual(expected, parse_puzzle_search_response(response))

        #search by play count
        lower, upper = 5, 10                                                                     
        response = puzzle_get(play_count=f'{lower}-{upper}')
        expected = [p.title for p in Puzzle.query.all() if lower<=p.play_count<=upper]
        self.assertCountEqual(expected, parse_puzzle_search_response(response))
        
        #sort by play count
        test_search_sort('play_count', lambda x: x.play_count)
        #sort by date
        test_search_sort('date', lambda x: x.dateCreated.timestamp())
        #sort by play count
        test_search_sort('rating', lambda x: x.average_rating)
        #sort by a-z
        test_search_sort('a-z', lambda x: x.title)
        #sort by highest score
        test_search_sort('highscore', lambda x: max([0] + [s.score for s in x.scores])) 

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
    
    def test_create_puzzle(self):
        '''
        Tests the puzzle creation endpoint.
        \nTests that an unauthenticated user cannot create a puzzle.
        \nTests that an authenticated user can create a puzzle, that the status code is correct, and that they are redirected correctly.
        '''
        #unauthenticated case
        self.assertCode(self.client.post(url_for(route.puzzle.create), data=dict(puzzlename="ENDPOINT_TEST_PUZZLE_ERROR", puzzle="ABCDEFGHI"), follow_redirects=False), 302)
        response = self.client.post(url_for(route.puzzle.create), data=dict(puzzlename="ENDPOINT_TEST_PUZZLE_ERROR", puzzle="ALKJLKLKJLKLKJLKJBCDEFGHI"), follow_redirects=True)
        self.assertEqual(url_for(route.login), response.request.path)

        #authenticated case
        self.t.register("POST_USER", "Valid123456")
        self.t.login("POST_USER", "Valid123456")
        response = self.assertCode(self.client.post(url_for(route.puzzle.create), data=dict(puzzlename="ENDPOINT_TEST_PUZZLE", puzzle="ABCDEFGHIJ"), follow_redirects=True), 200)
        self.assertEqual(url_for(route.index), response.request.path)
        self.assertIsNotNone(puzzle_utils.get_puzzle("ENDPOINT_TEST_PUZZLE"))

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
        self.assertCode(self.client.post(url_for(route.puzzle.rate, puzzleid=puzzle.id), json=dict(rating=2), follow_redirects=True), 401)
        #uncompleted case
        self.t.login("POST_USER", "123")
        self.assertCode(self.client.post(url_for(route.puzzle.rate, puzzleid=puzzle.id), json=dict(rating=2), follow_redirects=True), 401)
        #correct case
        puzzle.add_record(user, 50)
        response = self.assertCode(self.client.post(url_for(route.puzzle.rate, puzzleid=puzzle.id), json=dict(rating=2), follow_redirects=True), 200)
        #test average
        self.assertEqual(json.loads(response.data)['average_rating'], puzzle.average_rating)
        #404 (invalid puzzle) case
        self.assertCode(self.client.post(url_for(route.puzzle.rate, puzzleid=-1), json=dict(rating=2), follow_redirects=True), 404)

    def test_submit_score(self):
        pass