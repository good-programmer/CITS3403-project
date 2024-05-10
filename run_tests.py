import os
import unittest

from project import create_app
from project.config import TestingConfig

def clean():
    loc = TestingConfig.SQLALCHEMY_DATABASE_URI.replace('sqlite:///','')
    if os.path.isfile(os.path.abspath(loc)):
        os.remove(os.path.abspath(loc))
    if os.path.isfile(os.path.abspath(loc + '-journal')):
        os.remove(os.path.abspath(loc + '-journal'))

try:
    import tests

    app = create_app(TestingConfig)
    tests.app = app
    
    TestObject = tests.TestObject
    TestObject.numUsers = 20
    TestObject.numPuzzles = 40
    TestObject.numScores = 15
    TestObject.identifier = '$'
    TestObject.generate_username = tests.ordered_username
    TestObject.generate_puzzletitle = tests.ordered_puzzletitle
    tests.create_test_db(app=app)
    
    loader = unittest.TestLoader()
    start_dir = 'tests'
    suite = loader.discover(start_dir)

    runner = unittest.TextTestRunner()
    runner.run(suite)
finally: #clean up db files whether errored or not
    clean()