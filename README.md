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
Alternatively, you can execute the command `python3 -m unittest discover project/tests` from the same directory.

To migrate a database when `models.py` is updated (i.e. when the schema is changed), run `flask db migrate`, then `flask db upgrade`.