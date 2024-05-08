# CITS3403-project

|UWA ID  |Name          |Github Username|
|--------|--------------|---------------|
|21727658|Jack Donaghy  |good-programmer|
|23477174|Thomas Nguyen |tnguyen7523    |
|23402727|Nathan Buluran|naetnaetnaet   |
|22705919|Jakem Pinchin |JakePinchin    |

A website for uploading "Spelling Bee"-esque puzzles. Users can upload a set of letters (A-Z) and 'request' for other users to create words using combinations of the given letters. A leaderboard ranked by lengths of words could be created (in a limit, i.e. 5 words) for each puzzle that all users could view.
Users could rate each puzzle (by enjoyment or by difficulty).

Primary webpages include:
- login
- account registration
- landing page (for example, recently added / 'hot' puzzles)
- puzzle search page
- account profile editor
- (other) user profile view

The search page features:
- sort by creator name
- rating
- date created
- completed/incomplete
- popularity
- puzzle title (?)
- tags (?)

To start the app:

- `cd` into the repository directory (i.e. the directory of this README)
- `export FLASK_APP=project` to set the target app
- `export FLASK_SECRET_KEY=<your-key>` to set the private key for security purposes
- `export FLASK_DATABASE_URI=project/db/<your-database>` to set the database the app will connect to (see Databases section for more information)
- `flask run` to start the app (default 127.0.0.1:5000)

#Testing

To run tests, execute `run_tests.py` from CLI in the repository directory, i.e. `cd project_repository; python3 run_tests.py`.
This will create a transient in-memory database for testing purposes (which should take around 5sec on default settings), then run all tests.

#Databases

By default, the database used is `project/db/app.db`. It will be created if it does not exist when the app is started. To use or create a different database, see "Create a test database" below.

To migrate a database when `models.py` is updated (i.e. when the schema is changed), run `flask db migrate`, then `flask db upgrade`.

Update your current database (`app.db`):

- Find the version of the database that correctly matches yours (this may be hard to do - if your database was created just prior to commit 820a997, it should be identical to a90c7a8f4860. If it was created earlier, you may have to delete that database)
- Run `flask db stamp <your_version_here>`
- Now run `flask db upgrade`
- Repeat previous step until up-to-date (when the upgrade command no longer informs you of a version change)

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