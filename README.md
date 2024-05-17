# CITS3403-project

|UWA ID  |Name          |Github Username|
|--------|--------------|---------------|
|21727658|Jack Donaghy  |good-programmer|
|23477174|Thomas Nguyen |tnguyen7523    |
|23402727|Nathan Buluran|naetnaetnaet   |
|22705919|Jakem Pinchin |JakePinchin    |

A website for uploading "Spelling Bee"-esque puzzles. Users can upload a set of ten letters (A-Z) and 'request' for other users to create words using combinations of the given letters.
Others can solve these puzzles by inputting up to five words that use these letters and receive a score based on the total number of characters used.
Users can rate each puzzle (by enjoyment or by difficulty). For example, a puzzle that has a high variance could be seen as 'better' than a puzzle with low variance (i.e. 'AAAAAAAAAA').
Users can follow each other and access a follow-only leaderboard and view recent follow activity (i.e. followees' recent creations or ratings).
Users can search puzzles by name or creator, sort by date or rating, and filter by play count, completion status, date and more.

Primary webpages include:
- login
- account registration
- landing page (for example, recently added / 'hot' puzzles)
- puzzle search page
- user profiles
- puzzle profiles
- puzzle play page

## Getting started

These instructions are for a linux environment (native/vm/wsl).

Setting up a virtual environment:
- This app uses a number of external modules. You may want to keep these separate.
- Execute `python -m venv /path/to/env` to create the virtual environment.
- Execute `source <venv>/bin/activate` to activate the virtual environment
- Make sure you are in the repository directory (the directory of this README)
- Execute `pip install -r requirements.txt` to install dependencies.

To start the app:

- `cd` into the repository directory (the directory of this README)
- `export FLASK_APP=run.py` to set the target app
- `export FLASK_SECRET_KEY=<your-key>` to set the private key for security purposes
- (OPTIONAL) `export FLASK_DATABASE_URI=<your-database>` to override which database the app will connect to. Configs will have a default database target preset. (see Databases section for more information)
- `flask run` to start the app (default 127.0.0.1:5000)
- `run.py` by default executes the app in `default` configuration, which is (currently) equivalent to the 'development' config. See `/project/config.py` for the differences.
- You can change the config by setting the `FLASK_CONFIG` environment variable. Again see `/project/config.py` for available configs.
- To create dummy data, see "Create a test database" and "Generate test data" in the Databases section.
- **FOR MARKER** LMS upload comes with a pre-generated `test.db` in `project/db`

## Testing

To run tests, execute `run_tests.py` from CLI in the repository directory, i.e. `cd project_repository; python3 run_tests.py`.

This will create a temporary database for testing purposes (which should take around 5sec on default settings), then run all tests. This includes a unit test suite and a system (selenium) test suite.

You should *not* run individual tests with `python3 -m unittest tests` or similar. The database the tests rely on is only generated once for all tests, and methodically cleaned on tearDown. 

The alternative was to create and destroy the database before and after each test, which led to very large overhead for the number of tests performed (40+).

## Databases

By default, the database used is `project/db/test.db` - this is the default development database target. It will be created if it does not exist when the app is started.
    > `project/db/app.db` is the default production database target.

To use or create a different database, see "Create a test database" below.

Create a new database with the most recent schema:

- Run `flask shell` or `flask run`
- This will create the new database at the location indicated by FLASK_DATABASE_URI (if this is not set, the default target specified by the current config will be used).
- Close the shell / app
- Run `flask db stamp head`. This will tell flask-migrate that the new database is up to date.

Create a test database with the most recent schema:

- Set the test db environment variable: `export FLASK_DATABASE_URI=your/path/to/test.db`
- Then follow the above commands to create a new database.
- To revert to using default database, `unset FLASK_DATABASE_URI` to delete the environment variable.

Generate test data:

- Set the target database: `export FLASK_DATABASE_URI=your/path/to/the.db`. This should be a newly created, empty database with the most recent schema (upgrade if necessary).
- Execute `generate_test_data.py` from CLI in the repository directory and follow the prompts.

## Migrations

Migrations are located in `project/db/migrations`.

To migrate a database when `models.py` is updated (i.e. when the schema is changed), run `flask db migrate`, then `flask db upgrade`.

Update your current database:

- Find the version of the database that correctly matches yours (this may be hard to do - if your database was created just prior to commit 820a997, it should be identical to a90c7a8f4860. If it was created earlier, you may have to delete that database)
- Run `flask db stamp <your_version_here>`
- Now run `flask db upgrade`
- Repeat previous step until up-to-date (when the upgrade command no longer informs you of a version change)


## Credits

- [Bootstrap](https://getbootstrap.com/) and [jQuery](https://jquery.com/) for frontend visuals and design.
- Google and Peter Hull  for the [VT323](https://fonts.google.com/specimen/VT323) font.
- [Flask](https://flask.palletsprojects.com/en/3.0.x/) and its related packages for the web framework.
- [Selenium](https://www.selenium.dev/documentation/webdriver/) for system testing.
- Stackoverflow user [Temani Afif](https://stackoverflow.com/users/8620333/temani-afif) for their [CRT/Scanline .css background](https://stackoverflow.com/questions/61431316/how-to-get-scanlines-over-background-image-in-css)
- Codepen.io user [freelesio](https://codepen.io/freelesio) for their [Matrix Hacker Text Effect](https://codepen.io/freelesio/pen/MWQaGPb), which was modified for use in this project