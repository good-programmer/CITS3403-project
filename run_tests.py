import os
import unittest

prev = None
if 'FLASK_DATABASE_URI' in os.environ:
    prev = os.environ['FLASK_DATABASE_URI']

os.environ['FLASK_DATABASE_URI'] = "project/db/:memory:"

def clean():
    if os.path.isfile(os.path.abspath(os.environ['FLASK_DATABASE_URI'])):
        os.remove(os.path.abspath(os.environ['FLASK_DATABASE_URI']))
    if os.path.isfile(os.path.abspath(os.environ['FLASK_DATABASE_URI'] + '-journal')):
        os.remove(os.path.abspath(os.environ['FLASK_DATABASE_URI'] + '-journal'))
try:
    from project import tests
    tests.create_test_db()
    
    loader = unittest.TestLoader()
    start_dir = 'project/tests'
    suite = loader.discover(start_dir)

    runner = unittest.TextTestRunner()
    runner.run(suite)
finally: #clean up db files whether errored or not
    clean()
    if prev:
        os.environ['FLASK_DATABASE_URI'] = prev