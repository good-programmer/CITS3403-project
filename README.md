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


To run tests, execute `run_tests.py` from CLI in the `RequestProject` directory, i.e. `cd RequestProject; python3 run_tests.py`
Alternatively, you can execute the command `python3 -m unittest discover project/tests` from the same directory. *If you do this, make sure to `export FLASK_DATABASE_URI=:memory:` so your real database is not cleared!

To migrate a database when `models.py` is updated (i.e. when the schema is changed), run `flask db migrate`, then `flask db upgrade`.

To update your current database, follow these steps:

- Find the version of the database that correctly matches yours (this may be hard to do - if your database was created just prior to commit 820a997, it should be identical to a90c7a8f4860. If it was created earlier, you may have to delete that database)
- Run `flask db stamp <your_version_here>`
- Now run `flask db upgrade`
- Repeat previous step until up-to-date (when the upgrade command no longer informs you of a version change)

To create a new database with the most recent schema, follow these steps:

- Run `flask shell` or `flask run`
- This will create the new database (should be named app.db at time of writing).
- Close the shell / app
- Run `flask db stamp head`. This will tell flask-migrate that the new database is up to date.

To create a test database (with the most recent schema):

- Set the test db environment variable: export FLASK_DATABASE_URI=your/path/to/test.db
- Then run the commands to create a new database.
- To revert to using app.db, run unset FLASK_DATABASE_URI to delete the environment variable.