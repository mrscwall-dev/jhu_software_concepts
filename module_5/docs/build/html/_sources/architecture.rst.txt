Architecture
============

Grad Cafe Analytics is organized into three primary layers: the web layer,
the data processing layer, and the database/analysis layer.

Web Layer
---------

The Flask web application is implemented in ``src/app.py``.

The web layer is responsible for:

* Creating the Flask application.
* Rendering the Analysis page.
* Handling the Pull Data request.
* Handling the Update Analysis request.
* Preventing conflicting actions while a data pull is already running.
* Displaying analysis results to the user.

The application uses a ``create_app(...)`` factory so tests can provide
fake scraper, loader, and query functions.

Data Processing Layer
---------------------

The data processing layer contains the GradCafe scraping and cleaning
functions.

``src/scrape.py``
    Retrieves and parses GradCafe application records.

``src/clean.py``
    Prepares scraped records for additional processing.

``src/pull_data.py``
    Coordinates retrieving new records, standardizing data, updating JSON
    files, and inserting new records into PostgreSQL.

``src/load_data.py``
    Loads prepared applicant records into PostgreSQL.

Database and Analysis Layer
---------------------------

PostgreSQL is used to store applicant data.

``src/models.py``
    Defines the SQLAlchemy database model and database session.

``src/query_data.py``
    Contains analysis queries using PostgreSQL and psycopg.

``src/orm_queries.py``
    Contains analysis queries using SQLAlchemy ORM expressions.

The Flask application retrieves analysis results from the database and
passes them to the Analysis template for display.

Testing and Continuous Integration
----------------------------------

Automated tests are stored in ``module_4/tests``.

The suite includes:

* Flask page tests.
* Button and busy-state tests.
* Analysis formatting tests.
* Database tests.
* Integration tests.
* Tests for supporting application modules.

GitHub Actions runs the test suite automatically using PostgreSQL and the
same Pytest coverage requirements used locally.