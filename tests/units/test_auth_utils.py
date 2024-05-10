'''
validate_user_information
validate_puzzle_submit
'''
import unittest

from project.utils.auth_utils import *

class AuthUtilCase(unittest.TestCase):
    def setUp(self) -> None:
        return super().setUp()
    
    def tearDown(self) -> None:
        return super().tearDown()
    
    def test_validate_user_information(self):
        '''
        Username should be between 3 and 20 chars and contain alphanumerical and underscores only
        Password should be 4 chars or longer
        '''
        #usernames
        self.assertFalse(validate_user_information('ab','valid')[0]) #short name
        self.assertFalse(validate_user_information('a' * 21, 'valid')[0]) #long name
        self.assertFalse(validate_user_information('ab%#$#', 'valid')[0]) #invalid chars
        self.assertFalse(validate_user_information('a$', 'valid')[0]) #invalid + too short
        self.assertFalse(validate_user_information('a$' * 11, 'valid')[0]) #invalid + too long

        #passwords
        self.assertFalse(validate_user_information('valid', 'a2_')[0]) #short pass
        self.assertFalse(validate_user_information('valid', '')[0]) #very short pass

        #valid
        self.assertTrue(validate_user_information('valid', 'valid')[0])
        self.assertTrue(validate_user_information('__va__li__d__', 'valid1234!$@')[0])
    
    def test_validate_puzzle_submit(self):
        '''
        length: 10 chars
        chars: alphabet only
        '''
        self.assertFalse(validate_puzzle_submit('!@#$%6&*9)')[0]) #invalid chars
        self.assertFalse(validate_puzzle_submit('990123')[0]) #invalid chars
        self.assertFalse(validate_puzzle_submit('asdjkasnckdasnjckjsan')[0]) #too long
        self.assertFalse(validate_puzzle_submit('kvmmkxk')[0]) #too short
        self.assertFalse(validate_puzzle_submit('sodc9kz!')[0]) #too short + invalid
        self.assertFalse(validate_puzzle_submit('asdj$#$%k&*&njkjsan')[0]) #too long + invalid

        # Test for correct string
        self.assertTrue(validate_puzzle_submit('SSAAMCDDKL')[0])
        self.assertTrue(validate_puzzle_submit('kasdjflkas')[0])
