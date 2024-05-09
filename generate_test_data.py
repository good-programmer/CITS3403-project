def valid_int_input(msg):
    inp = input(msg)
    while not inp.isdecimal():
        print('Not an integer.')
        inp = input(msg)
    print('OK')
    return int(inp)

def generate():
    import os
    
    
    print('This is the test data generation utility tool.')
    print('The target database should be empty. If not, the tool may fail or corrupt the database.')
    print('Current target: ' + os.path.abspath(os.environ.get('FLASK_DATABASE_URI', 'project/db/app.db')))
    option = input('Y to continue, C to change target/create new database, any other key to exit\n').upper()
    if option == 'C':
        url = input('Enter path to database (if it does not exist, it will be created): ')
        print('Target database: ' + os.path.abspath(url))
        os.environ['FLASK_DATABASE_URI'] = url
    elif option != 'Y':
        return
    print('')
    print('Enter generation options')
    users = valid_int_input("Number of users: ")
    puzzles =  valid_int_input("Number of puzzles: ")
    scores = valid_int_input("Max user scores and ratings per puzzle (LIMIT: number of users): ")

    from project import create_app
    from project.config import configurations
    app = create_app(configurations['development'])

    from project.tests import create_test_db, random_username, random_puzzletitle, TestObject
    TestObject.numUsers = users
    TestObject.numPuzzles = puzzles
    TestObject.numScores = scores
    TestObject.numRatings = scores
    TestObject.identifier = ''
    TestObject.generate_username = random_username
    TestObject.generate_puzzletitle = random_puzzletitle

    input('ENTER to begin generating, CTRL+C to quit.')
    create_test_db(app=app, msg='Generating data...')

if __name__ == '__main__':
    generate()