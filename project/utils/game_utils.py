from ..config import PATH
import os

# read the words from the file into a set
words = os.path.join(PATH, 'utils', 'words_dict')
with open(words, 'r') as f:
    valid_words = set(word.strip() for word in f)

def dict_check_input(user_input):
        # check if the user's input is a valid word
        return user_input.lower() in valid_words
