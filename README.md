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

To start the app:

- `cd` into the repository directory (i.e. the directory of this README)
- `export FLASK_APP=run.py` to set the target app
- `export FLASK_SECRET_KEY=<your-key>` to set the private key for security purposes
- `export FLASK_DATABASE_URI=<your-database>` to set the database the app will connect to (optional, see Databases section for more information)
- `flask run` to start the app (default 127.0.0.1:5000)

## Testing

To run tests, execute `run_tests.py` from CLI in the repository directory, i.e. `cd project_repository; python3 run_tests.py`.
This will create a transient in-memory database for testing purposes (which should take around 5sec on default settings), then run all tests. This includes a unit test suite and a system (selenium) test suite.
You should *not* run individual test by running `python3 -m unittest tests` or similar. The database the tests rely on is only generated once for all tests, and efficiently cleaned on tearDown. 
The alternative was to create and destroy the database before and after each test, which led to very large overhead for the number of tests performed (40+).

## Databases

By default, the database used is `project/db/app.db`. It will be created if it does not exist when the app is started. To use or create a different database, see "Create a test database" below.

Create a new database with the most recent schema:

- Run `flask shell` or `flask run`
- This will create the new database.
- Close the shell / app
- Run `flask db stamp head`. This will tell flask-migrate that the new database is up to date.

Create a test database with the most recent schema:

- Set the test db environment variable: `export FLASK_DATABASE_URI=your/path/to/test.db`
- Then run the commands to create a new database.
- To revert to using app.db, run unset FLASK_DATABASE_URI to delete the environment variable.

Generate test data:

- Set the target database: `export FLASK_DATABASE_URI=your/path/to/test.db`. This should be a newly created, empty database with the most recent schema (upgrade if necessary).
- Execute `generate_test_data.py` from CLI in the repository directory and follow the prompts.

## Migrations
To migrate a database when `models.py` is updated (i.e. when the schema is changed), run `flask db migrate`, then `flask db upgrade`.

Update your current database (`app.db`):

- Find the version of the database that correctly matches yours (this may be hard to do - if your database was created just prior to commit 820a997, it should be identical to a90c7a8f4860. If it was created earlier, you may have to delete that database)
- Run `flask db stamp <your_version_here>`
- Now run `flask db upgrade`
- Repeat previous step until up-to-date (when the upgrade command no longer informs you of a version change)