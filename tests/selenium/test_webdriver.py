from selenium import webdriver
import tests.selenium

class ChromeWebDriverCase(tests.selenium.WebDriverCase):
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
class EdgeWebDriverCase(WebDriverCase):
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

class FirefoxWebDriverCase(WebDriverCase):
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