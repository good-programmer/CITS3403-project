from ..config import PATH
import os
import re

# read the words from the file into a set
words = os.path.join(PATH, 'utils', 'words_dict')
with open(words, 'r') as f:
    valid_words = set(word.strip() for word in f)

# sanitise string; check it is contained in valid_words
def validate_input(user_input):
        sanitised = sanitise_input(user_input)
        # check if the user's input is a valid word
        return sanitised.upper() in valid_words

def words_in_puzzle_string(submittedWords, puzzleString):
    for word in submittedWords:
        temp_string = puzzleString
        for letter in word:
                if letter in temp_string:
                    temp_string = temp_string.replace(letter, '', 1)
                else:
                    return False
    return True

# remove non-alphabetic characters and ensure string is lowercase
def sanitise_input(user_input):
    sanitised_input = re.sub('[^a-z]', '', user_input.lower())
    return sanitised_input

# verify the score of a user's puzzle solution
def verify_score(submittedWords, puzzleString):
    sanitised_words = [sanitise_input(word) for word in submittedWords]

    if len(submittedWords) <=5:
        if all(validate_input(word) for word in sanitised_words):
            if words_in_puzzle_string(sanitised_words, puzzleString.lower()):
                score = sum(len(word) for word in sanitised_words)
                print(score)
                return score

    return None

    