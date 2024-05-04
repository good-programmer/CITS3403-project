def valid_int_input(msg):
    inp = input(msg)
    while not inp.isdecimal():
        print('Not an integer.')
        inp = input(msg)
    print('OK')
    return int(inp)

def generate():
    from project.config import Config
    from project.tests import create_test_db, random_username, random_puzzletitle, TestObject

    print('This is the test data generation utility tool.')
    print('The target database should be empty. If not, the tool may fail or corrupt the database.')
    print('You can change the target by running `export FLASK_DATABASE_URI=your/path/to/database` in CLI')
    print('Current target: ' + Config.SQLALCHEMY_DATABASE_URI)
    input('ENTER to continue')
    print('')
    print('Enter generation options')
    users = valid_int_input("Number of users: ")
    puzzles =  valid_int_input("Number of puzzles: ")
    scores = valid_int_input("Max user scores and ratings per puzzle (LIMIT: number of users): ")

    TestObject.numUsers = users
    TestObject.numPuzzles = puzzles
    TestObject.numScores = scores
    TestObject.numRatings = scores
    TestObject.identifier = ''
    TestObject.generate_username = random_username
    TestObject.generate_puzzletitle = random_puzzletitle

    input('ENTER to begin generating, CTRL+C to quit.')
    create_test_db('Generating data...')

if __name__ == '__main__':
    generate()