import multiprocessing.process
import unittest, multiprocessing, logging

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

from flask import url_for, cli 

from tests import TestObject, app

from project import db
from project.utils import user_utils, puzzle_utils, route_utils as route

logging.getLogger("werkzeug").disabled = True
cli.show_server_banner = lambda *args: None

localhost = "http://127.0.0.1:5000"

class WebDriverCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app_context = app.test_request_context()
        cls.app_context.push()
        cls.client = app.test_client()
        cls.t = TestObject(app, db)
        cls.t.add_test_client(cls.client) 

        return super().setUpClass()

    def get_driver(self) -> webdriver.Chrome:
        return self.__class__.driver

    def setUp(self):
        self.server_thread = multiprocessing.Process(target=lambda: app.run(debug=False, use_reloader=False))
        self.server_thread.start()

    def tearDown(self):
        self.get_driver().delete_all_cookies()
        self.server_thread.terminate()
        self.server_thread.join()
        
        self.t.clear_db()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.app_context.pop()
        return super().tearDownClass()
    
    def emulate_register(self, username, password, confirm_password):
        '''Grouped steps involved in registering a new user'''
        driver = self.get_driver()
        driver.get(localhost + url_for(route.register))
        driver.find_element(By.ID, "username-input").clear()
        driver.find_element(By.ID, "username-input").send_keys(username)
        driver.find_element(By.ID, "password-input").send_keys(password)
        driver.find_element(By.ID, "confirm-password-input").send_keys(confirm_password)
        driver.find_element(By.ID, "submit").click()
    
    def emulate_login(self, username, password):
        '''Grouped steps involved in logging in a user'''
        driver = self.get_driver()
        driver.get(localhost + url_for(route.login))
        driver.find_element(By.ID, "username-input").clear()
        driver.find_element(By.ID, "username-input").send_keys(username)
        driver.find_element(By.ID, "password-input").send_keys(password)
        driver.find_element(By.ID, "submit").click()
    
    def test_register(self):
        driver = self.get_driver()
        el = lambda: driver.find_elements(By.CSS_SELECTOR, ".error-message")

        #invalid cases, should flash an error msg
        self.emulate_register("t","12345","12345")
        self.assertEqual(el()[0].text, 'Username must be between 3 and 20 characters')
        self.emulate_register("!testr!","12345","12345")
        self.assertEqual(el()[0].text, 'Username must contain only letters, numbers and _')
        self.emulate_register("testr","123","123")
        self.assertEqual(el()[0].text, 'Password must be 4 characters or longer')
        self.emulate_register("testr","12345","abcde")
        self.assertEqual(el()[0].text, 'Passwords do not match')

        #should register successfully and redirect to login
        self.emulate_register("testr","12345","12345")
        self.assertEqual(driver.current_url, localhost + url_for(route.login))
    
    def test_login(self):
        driver = self.get_driver()
        self.emulate_register("testl","12345","12345")
        el = lambda: driver.find_elements(By.CSS_SELECTOR, ".error-message")

        #invalid cases, should flash an error msg
        self.emulate_login("!testl!","12345")
        self.assertEqual(el()[0].text, 'Incorrect username or password')
        self.emulate_login("testl","abcde")
        self.assertEqual(el()[0].text, 'Incorrect username or password')

        #empty fields, shouldn't flash an error msg but show a warning
        self.emulate_login("testl","")
        self.emulate_login("","12345")
        self.assertEqual(driver.current_url, localhost + url_for(route.login))

        #should login successfully and redirect to user's profile page
        self.emulate_login("testl","12345")
        self.assertEqual(driver.current_url, localhost + url_for(route.user.profile, userid=21))

    def test_navbar(self):
        driver = self.get_driver()

        #not logged in, should only display Home|Login|Register
        driver.get(localhost + url_for(route.user.profile, userid=1))
        links = [a.text for a in driver.find_elements(By.CSS_SELECTOR, ".navbar a")]
        self.assertListEqual(['Home', 'About', 'Login', 'Register'], links)

        #logged in, should display Home|Random|Submit Puzzle|Profile|Logout
        self.emulate_login("$GENERATED_USER_0", "123")
        driver.get(localhost + url_for(route.user.profile, userid=1))
        links = [a.text for a in driver.find_elements(By.CSS_SELECTOR, ".navbar a")]
        self.assertListEqual(['Home', 'About', 'Random', 'Search', 'Create', 'Profile', 'Logout'], links)


    def test_landing(self):
        driver = self.get_driver()
        driver.get(localhost)

        #not logged in
        self.assertIn("word-amble", driver.title)
        self.assertEqual(driver.find_element(By.XPATH,"//a[contains(text(),'Login')]").text, 'Login')
        self.assertEqual(driver.find_element(By.XPATH,"//a[contains(text(),'Register')]").text, 'Register')

        #logged in
        self.emulate_register("test", "12345", "12345")
        self.emulate_login("test", "12345")

        driver.get(localhost)
        self.assertEqual(driver.find_element(By.XPATH,"//a[contains(text(),'Profile')]").text, 'Profile')
        self.assertRaises(NoSuchElementException, driver.find_element, By.XPATH, "//a[contains(text(),'Login')]")
        self.assertRaises(NoSuchElementException, driver.find_element, By.XPATH, "//a[contains(text(),'Register')]")
    
    def test_profile(self):
        driver = self.get_driver()
        driver.get(localhost + url_for(route.user.profile, userid=1))
        user, user2 = user_utils.get_user(id=1), user_utils.get_user(id=2)

        #follow button does not exist
        self.assertIn("Log in to follow", driver.page_source)
        self.assertRaises(NoSuchElementException, driver.find_element, By.CSS_SELECTOR, "#follow-button")
        #basic info
        self.assertIn(user.name, driver.page_source)
        self.assertIn(f"total_completed_puzzles: {len(user.scores)}", driver.page_source)
        self.assertIn(f"total_ratings: {len(user.ratings)}", driver.page_source)
        self.assertIn(f"total_created puzzles: {len(user.puzzles)}", driver.page_source)
        self.assertIn(f"following: {len(user.following)}", driver.page_source)
        self.assertIn(f"followers: {len(user.followers)}", driver.page_source)
        #list lengths match number of puzzles/scores/ratings
        self.assertEqual(len(driver.find_elements(By.CSS_SELECTOR, "#created-list > .post-body")), len(user.puzzles))
        self.assertEqual(len(driver.find_elements(By.CSS_SELECTOR, "#completed-list > .post-body")), len(user.scores))
        self.assertEqual(len(driver.find_elements(By.CSS_SELECTOR, "#rated-list > .post-body")), len(user.ratings))

        #test pressing the follow button
        user2.unfollow_user(user)
        self.emulate_login(user2.name, "123")
        driver.get(localhost + url_for(route.user.profile, userid=1))
        follow = driver.find_element(By.CSS_SELECTOR, "#follow-button")
        self.assertEqual(follow.text, "[FOLLOW]")
        follow.click()
        WebDriverWait(driver, 2).until(expected_conditions.text_to_be_present_in_element((By.CSS_SELECTOR, "#follow-button"), "[UNFOLLOW]"))
        self.assertTrue(user2.is_following(user))
        self.assertEqual(follow.text, "[UNFOLLOW]")
        follow.click()
        WebDriverWait(driver, 2).until(expected_conditions.text_to_be_present_in_element((By.CSS_SELECTOR, "#follow-button"), "[FOLLOW]"))
        self.assertFalse(user2.is_following(user))
        self.assertEqual(follow.text, "[FOLLOW]")

    def test_puzzle_info(self):
        driver = self.get_driver()
        puzzle = puzzle_utils.get_puzzle(id=1)
        user = user_utils.get_user(id=1)
        if puzzle.has_record(user): 
            puzzle.remove_record(user)
        driver.get(localhost + url_for(route.puzzle.info, puzzleid=1))
        
        #basic info
        self.assertIn(puzzle.title, driver.page_source)
        self.assertIn(puzzle.creator.name, driver.page_source)
        self.assertIn(f"plays: {len(puzzle.scores)}", driver.page_source)
        self.assertIn(f"highest_score: {puzzle.highest_score}", driver.page_source)
        self.assertIn(f"date_created: {str(puzzle.dateCreated)[:10]}", driver.page_source)
        self.assertIn(f"average_rating: {round(puzzle.average_rating, 2)}", driver.page_source)
        self.assertEqual(len(driver.find_elements(By.CSS_SELECTOR, "#main-leaderboard > .post-body")), len(puzzle.scores))

        #disabled/invisible elements when not logged in
        self.assertTrue(driver.find_element(By.CSS_SELECTOR, "#play-button").get_property("disabled"))
        self.assertIn("display: none", driver.find_element(By.CSS_SELECTOR, "#rate-section").get_attribute("style"))

        #logged in, no record
        self.emulate_login(user.name, "123")
        driver.get(localhost + url_for(route.puzzle.info, puzzleid=puzzle.id))
        self.assertIsNone(driver.find_element(By.CSS_SELECTOR, "#play-button").get_attribute("disabled"))
        self.assertNotIn("display: none", driver.find_element(By.CSS_SELECTOR, "#rate-section").get_attribute("style"))
        self.assertIn("disabled", driver.find_element(By.CSS_SELECTOR, "#rate-slider").get_attribute("class"))
        self.assertNotIn(user.name, driver.find_element(By.CSS_SELECTOR, ".leaderboard-body").get_property("innerHTML"))

        #logged in, record
        puzzle.add_record(user, 10)
        driver.refresh()
        self.assertTrue(driver.find_element(By.CSS_SELECTOR, "#play-button").get_attribute("disabled"))
        self.assertNotIn("disabled", driver.find_element(By.CSS_SELECTOR, "#rate-slider").get_attribute("class"))
        self.assertIn(user.name, driver.find_element(By.CSS_SELECTOR, "#main-leaderboard").get_property("innerHTML"))
        self.assertIn(user.name, driver.find_element(By.CSS_SELECTOR, "#following-leaderboard").get_property("innerHTML"))

    def test_submit_puzzle(self):
        driver = self.get_driver()
        user = user_utils.get_user(id=1)
        self.emulate_login(user.name, "123")
        driver.get(localhost + url_for(route.puzzle.create))

        #invalid content length
        driver.find_element(By.CSS_SELECTOR, "#puzzle-name-input").click()
        driver.find_element(By.CSS_SELECTOR, "#puzzlename").send_keys("test")
        driver.find_element(By.CSS_SELECTOR, "#content-box").click()
        driver.find_element(By.CSS_SELECTOR, "#puzzle").send_keys("abcd")
        driver.find_element(By.CSS_SELECTOR, '#create-puzzle-btn').click()
        self.assertIsNone(puzzle_utils.get_puzzle(title="test"))

        #invalid chars
        driver.find_element(By.CSS_SELECTOR, "#content-box").click()
        driver.find_element(By.CSS_SELECTOR, "#puzzle").send_keys("@#FS329fa5")
        driver.find_element(By.CSS_SELECTOR, '#create-puzzle-btn').click()
        self.assertIsNone(puzzle_utils.get_puzzle(title="test"))
        
        #valid content
        driver.find_element(By.CSS_SELECTOR, "#content-box").click()
        driver.find_element(By.CSS_SELECTOR, "#puzzle").send_keys("abcdef")
        driver.find_element(By.CSS_SELECTOR, '#create-puzzle-btn').click()
        WebDriverWait(driver, 2).until(expected_conditions.url_changes(localhost + url_for(route.puzzle.create)))
        self.assertEqual(driver.current_url, localhost + url_for(route.puzzle.info, puzzleid=41))
        self.assertIsNotNone(puzzle_utils.get_puzzle(title="test"))

    def test_game(self):
        driver = self.get_driver()
        user = user_utils.get_user(id=1)
        puzzle = puzzle_utils.add_puzzle("test", user, "ABCMNOSTUV")
        self.emulate_login(user.name, "123")
        driver.get(localhost + url_for(route.puzzle.play, puzzleid=puzzle.id))

        content = puzzle.content.upper()
        WebDriverWait(driver, 2).until(expected_conditions.text_to_be_present_in_element((By.CSS_SELECTOR, "#puzzleString"), puzzle.content))
        ps = driver.find_element(By.CSS_SELECTOR, "#puzzleString")
        inp = driver.find_element(By.CSS_SELECTOR, "#userInput")
        sub = driver.find_element(By.CSS_SELECTOR, "#submittedWords")

        #series of valid and invalid key into the input box
        self.assertEqual(ps.text, content)
        inp.send_keys("a")
        content = content.replace('A','',1)
        self.assertEqual(ps.text, content)
        inp.send_keys("axyz")
        self.assertEqual(ps.text, content)
        inp.send_keys("ct")
        c1 = content.replace('C','',1)
        content = c1.replace('T','',1)
        self.assertEqual(ps.text, content)
        inp.send_keys(Keys.BACK_SPACE)
        self.assertEqual(ps.text, c1)
        inp.send_keys("t")
        inp.send_keys(Keys.ENTER)
        self.assertEqual(inp.text, "")

        #test score and submission
        self.assertIn("act", sub.get_property("innerHTML"))
        self.assertEqual("3", driver.find_element(By.CSS_SELECTOR, "#scoreValue").text)
        driver.find_element(By.CSS_SELECTOR, "#submitButton").click()
        WebDriverWait(driver, 2).until(expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, "#leaderboard")))
        self.assertTrue(puzzle.has_record(user))
        
    def test_search(self):
        pass