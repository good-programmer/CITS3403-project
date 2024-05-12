import multiprocessing.process
import unittest, multiprocessing

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from flask import url_for

from tests import TestObject, app

from project import db
from project.utils import route_utils as route

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
        driver = self.get_driver()
        driver.get(localhost + url_for(route.register))
        driver.find_element(By.ID, "username-input").clear()
        driver.find_element(By.ID, "username-input").send_keys(username)
        driver.find_element(By.ID, "password-input").send_keys(password)
        driver.find_element(By.ID, "confirm-password-input").send_keys(confirm_password)
        driver.find_element(By.ID, "submit").click()
    
    def emulate_login(self, username, password):
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
        links = [a.text for a in driver.find_elements(By.CSS_SELECTOR, ".header > a")]
        self.assertListEqual(['Home', 'Login', 'Register'], links)

        #logged in, should display Home|Random|Submit Puzzle|Profile|Logout
        self.emulate_login("$GENERATED_USER_0", "123")
        driver.get(localhost + url_for(route.user.profile, userid=1))
        links = [a.text for a in driver.find_elements(By.CSS_SELECTOR, ".header > a")]
        self.assertListEqual(['Home', 'Random', 'Submit Puzzle', 'Profile', 'Logout'], links)


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
        self.assertIn("Log in to follow", driver.page_source)

    def test_puzzle_info(self):
        pass

    def test_submit_puzzle(self):
        pass

    def test_game(self):
        pass