import multiprocessing.process
import unittest, multiprocessing

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from tests import TestObject, app

from project import db

localhost = "http://127.0.0.1:5000/"

class WebDriverCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app_context = app.app_context()
        cls.app_context.push()
        cls.t = TestObject(app, db)

        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        cls.driver = webdriver.Chrome(options=options)

        return super().setUpClass()

    def setUp(self):
        self.server_thread = multiprocessing.Process(target=lambda: app.run(debug=False, use_reloader=False))
        self.server_thread.start()

    def tearDown(self):
        self.server_thread.terminate()
        self.server_thread.join()
        
        self.t.clear_db()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.driver.close()
        cls.driver.quit()
        cls.app_context.pop()
        return super().tearDownClass()
    
    def test_search(self):
        driver = self.driver
        driver.get(localhost)
        self.assertIn("word-amble", driver.title)