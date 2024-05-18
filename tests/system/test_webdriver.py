from selenium import webdriver
import tests.system

class ChromeWebDriverCase(tests.system.WebDriverCase):
    @classmethod
    def setUpClass(cls) -> None:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        cls.driver = webdriver.Chrome(options=options)

        super().setUpClass()
    
    @classmethod
    def tearDownClass(cls) -> None:
        cls.driver.close()
        cls.driver.quit()

        super().tearDownClass()

#---------------------------------Other browsers---------------------------------
'''
class EdgeWebDriverCase(tests.system.WebDriverCase):
    @classmethod
    def setUpClass(cls) -> None:
        options = webdriver.EdgeOptions()
        options.add_argument("--headless=new")
        cls.driver = webdriver.Edge(options=options)

        super().setUpClass()
    
    @classmethod
    def tearDownClass(cls) -> None:
        cls.driver.close()
        cls.driver.quit()
        
        super().tearDownClass()

class FirefoxWebDriverCase(tests.system.WebDriverCase):
    @classmethod
    def setUpClass(cls) -> None:
        options = webdriver.FirefoxOptions()
        options.add_argument("--headless")
        cls.driver = webdriver.Firefox(options=options)

        super().setUpClass()
    
    @classmethod
    def tearDownClass(cls) -> None:
        cls.driver.close()
        cls.driver.quit()
        
        super().tearDownClass()
'''