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

# remove non-alphabetic characters and ensure string is lowercase
def sanitise_input(user_input):
    sanitised_input = re.sub('[^a-z]', '', user_input.lower())
    return sanitised_input

# verify the score of a user's puzzle solution
def verify_score(submittedWords):
    total_score = 0
    for word in submittedWords:
        if validate_input(word):
            total_score += len(word)
    return total_score

    