import os
import unittest

os.environ['FLASK_DATABASE_URI'] = "project/db/unittest.db"

loader = unittest.TestLoader()
start_dir = 'project/tests'
suite = loader.discover(start_dir)

runner = unittest.TextTestRunner()
runner.run(suite)

os.remove(os.path.abspath(os.environ['FLASK_DATABASE_URI']))