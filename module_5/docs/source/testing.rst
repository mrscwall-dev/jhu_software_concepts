Testing Guide
=============

Pytest
------

Module 4 uses Pytest for automated testing.

All tests are stored in::

    module_4/tests/

The Pytest configuration is stored in::

    module_4/pytest.ini

Required Markers
----------------

Every test uses one or more of the following markers:

``web``
    Flask page loading and HTML structure.

``buttons``
    Pull Data and Update Analysis behavior.

``analysis``
    Analysis labels and percentage formatting.

``db``
    Database schema, inserts, and queries.

``integration``
    End-to-end application behavior.

Run the Full Test Suite
-----------------------

From the repository root, run::

    pytest module_4/tests -c module_4/pytest.ini -m "web or buttons or analysis or db or integration"

Coverage
--------

The project uses ``pytest-cov`` and requires 100 percent coverage for code
under ``module_4/src``.

The successful coverage output is stored in::

    module_4/coverage_summary.txt

Stable Selectors
----------------

The Flask page provides stable selectors for button tests.

The Pull Data button uses::

    data-testid="pull-data-btn"

The Update Analysis button uses::

    data-testid="update-analysis-btn"

Test Doubles and Fixtures
-------------------------

Tests use fixtures, fake functions, and monkeypatching so they can run
without live internet access or long-running GradCafe scraping.

Examples include:

* Fake scraper functions.
* Fake loader functions.
* Fake query functions.
* Flask's test client.
* Temporary database state.
* Monkeypatched application dependencies.

Database Testing
----------------

Database and integration tests use the PostgreSQL database::

    gradcafe_test

Tests verify database inserts, uniqueness behavior, and analysis queries.

Continuous Integration
----------------------

GitHub Actions runs the full test suite automatically.

The workflow is located at::

    .github/workflows/tests.yml

The workflow starts PostgreSQL, installs the project requirements, and
runs the marked Pytest suite with coverage.