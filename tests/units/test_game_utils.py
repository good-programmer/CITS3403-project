'''
validate_input
words_in_puzzle_string
sanitise_input
verify_score
'''

import unittest

from project.utils.game_utils import *

class GameUtilCase(unittest.TestCase):
    def setUp(self) -> None:
        return super().setUp()
    
    def tearDown(self) -> None:
        return super().tearDown()
    
    def test_sanitise_input(self):
        expected = 'abcdefg'

        #order after filter is correct
        self.assertEqual(expected, sanitise_input('ABCdeFG'))
        self.assertEqual(expected, sanitise_input('ABc12#%$%@#@#dEFg'))
        self.assertEqual(expected, sanitise_input('a b c__d e  f\ng'))
        self.assertEqual(expected, sanitise_input('abcdefg'))
        #order after filter is incorrect
        self.assertNotEqual(expected, sanitise_input(''))
        self.assertNotEqual(expected, sanitise_input('ABcFGed'))
    
    def test_validate_input(self):
        #correct after filter
        self.assertTrue(validate_input('cat'))
        self.assertTrue(validate_input('cAt'))
        self.assertTrue(validate_input('c A t'))
        self.assertTrue(validate_input('c$$##A__#@^t'))
        #incorrect after filter
        self.assertFalse(validate_input(''))
        self.assertFalse(validate_input('cxt'))
        self.assertFalse(validate_input('c$##$x__t'))
    
    def test_words_in_puzzle_string(self):
        puzzleString = 'ABCDEOIST'

        #all letters are in puzzle string
        self.assertTrue(words_in_puzzle_string(['BAD', 'SAD', 'CAB'], puzzleString))
        self.assertTrue(words_in_puzzle_string(['BAD', 'DST', 'CAB'], puzzleString))
        #not all letter(s) are in puzzle string
        self.assertFalse(words_in_puzzle_string(['BAD', 'MAT', 'CAB'], puzzleString))
        self.assertFalse(words_in_puzzle_string(['BAD', 'XZT', 'CAB'], puzzleString))
    
    def test_verify_score(self):
        puzzleString = 'ABCDEOIST'

        #after sanitising, results in valid word
        self.assertEqual(verify_score(['BAD', 'CABS'], puzzleString), 7)
        self.assertEqual(verify_score(['BAD', 'SAD', 'CAB'], puzzleString), 9)
        self.assertEqual(verify_score(['BA__&&&D', 'S  A D', 'CaB'], puzzleString), 9)
        #after sanitising, still invalid words
        self.assertEqual(verify_score(['BAD', 'MAT', 'CAB'], puzzleString), None)
        self.assertEqual(verify_score(['BAD', 'DST', 'CAB'], puzzleString), None)
        self.assertEqual(verify_score(['BAD', 'XZT', 'CAB'], puzzleString), None)