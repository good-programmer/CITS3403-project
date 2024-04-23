import unittest
loader = unittest.TestLoader()
start_dir = 'project/tests'
suite = loader.discover(start_dir)

runner = unittest.TextTestRunner()
runner.run(suite)