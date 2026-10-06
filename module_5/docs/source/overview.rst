Overview and Setup
==================

Project Overview
----------------

Grad Cafe Analytics is a Python application that collects, cleans, stores,
and analyzes graduate admissions information.

The application includes:

* A Flask analysis page.
* A Pull Data function for retrieving new GradCafe records.
* PostgreSQL database storage.
* SQLAlchemy and SQL-based analysis queries.
* Automated Pytest testing.
* GitHub Actions continuous integration.
* Sphinx documentation.

Project Structure
-----------------

The main Module 4 project structure is::

    module_4/
        src/
        tests/
        docs/
        pytest.ini
        requirements.txt
        README.md
        coverage_summary.txt
        actions_success.png

Install Requirements
--------------------

From the repository root, move into the Module 4 folder::

    cd module_4

Install the required Python packages::

    python3 -m pip install -r requirements.txt

PostgreSQL
----------

The application uses PostgreSQL.

The default application database is::

    gradcafe

The test suite uses::

    gradcafe_test

The application supports the ``DATABASE_URL`` environment variable for
database configuration.

For example::

    export DATABASE_URL="postgresql+psycopg://localhost/gradcafe"

Run the Flask Application
-------------------------

From the ``module_4`` folder, run::

    python3 -m src.app

The Flask application runs on port 5001.

Open the application in a browser at::

    http://127.0.0.1:5001/analysis

Run Tests
---------

From the repository root, run::

    pytest module_4/tests -c module_4/pytest.ini -m "web or buttons or analysis or db or integration"

The Module 4 test suite is configured to require 100 percent test coverage.

GitHub Actions
--------------

The GitHub Actions workflow is located at::

    .github/workflows/tests.yml

The workflow starts PostgreSQL, installs project requirements, and runs the
full marked Pytest suite with coverage.