# Module 4 - Pytest, Continuous Integration, and Sphinx Documentation

## Overview

This project builds on the Grad Café Analytics application developed in Module 3.

Module 4 adds automated testing with Pytest, 100% test coverage with pytest-cov, continuous integration with GitHub Actions, and Sphinx documentation published through Read the Docs.

The application includes:

- A Flask Analysis webpage
- Pull Data and Update Analysis functionality
- PostgreSQL database storage
- Raw SQL and SQLAlchemy analysis queries
- Grad Café data processing
- Automated unit and integration tests
- 100% test coverage
- GitHub Actions continuous integration
- Sphinx documentation

## Repository

GitHub repository:

```text
git@github.com:mrscwall-dev/jhu_software_concepts.git
```

## Project Structure

```text
module_4/
    src/                    Application source code
    tests/                  Pytest test suite
    docs/                   Sphinx documentation
    pytest.ini              Pytest and coverage configuration
    requirements.txt        Python dependencies
    README.md               Module 4 project documentation
    coverage_summary.txt    Successful 100% coverage output
    actions_success.png     Successful GitHub Actions screenshot
```

## Requirements

Python 3.12 is used for this project.

Install the required Python packages from the repository root:

```bash
python3 -m pip install -r module_4/requirements.txt
```

PostgreSQL must also be installed and running.

The application uses a PostgreSQL database named:

```text
gradcafe
```

The automated database tests use:

```text
gradcafe_test
```

The application supports the `DATABASE_URL` environment variable for PostgreSQL configuration.

Database passwords, API keys, and other credentials should not be committed to the repository.

## Source Files

Application code is located under `module_4/src/`.

- `app.py` - Creates and runs the Flask application.
- `scrape.py` - Retrieves and parses Grad Café records.
- `clean.py` - Prepares scraped data for processing.
- `load_data.py` - Loads prepared applicant records into PostgreSQL.
- `models.py` - Defines the SQLAlchemy Applicant model and database session.
- `query_data.py` - Performs analysis using raw SQL and psycopg.
- `orm_queries.py` - Performs selected analyses using SQLAlchemy.
- `pull_data.py` - Coordinates retrieving, processing, and storing new Grad Café records.
- `templates/analysis.html` - Displays the Flask Analysis page.
- `static/style.css` - Provides webpage styling.

## Run the Application

From the repository root, move into the Module 4 folder:

```bash
cd module_4
```

Run the Flask application:

```bash
python3 -m src.app
```

The application runs on port 5001.

Open the Analysis page in a browser at:

```text
http://127.0.0.1:5001/analysis
```

The **Pull Data** button checks for newly available Grad Café records.

The **Update Analysis** button refreshes the displayed analysis using the current PostgreSQL data.

The application prevents conflicting requests while a Pull Data operation is already running.

## Load the Database

From the `module_4` folder, run:

```bash
python3 -m src.load_data
```

The loader creates the applicants table when needed and loads the prepared applicant records into PostgreSQL.

Existing `p_id` values are not inserted again.

## Run Raw SQL Analysis

From the `module_4` folder, run:

```bash
python3 -m src.query_data
```

This executes the Grad Café analysis using raw SQL and psycopg.

## Run SQLAlchemy Analysis

From the `module_4` folder, run:

```bash
python3 -m src.orm_queries
```

This performs selected analyses using SQLAlchemy.

## Pull New Grad Café Data

From the `module_4` folder, run:

```bash
python3 -m src.pull_data
```

The Pull Data process checks for Grad Café records that are not already stored in PostgreSQL, processes the new records, and inserts new records into the database.

## Automated Testing

Pytest tests are stored in:

```text
module_4/tests/
```

The required Pytest markers are:

- `web`
- `buttons`
- `analysis`
- `db`
- `integration`

From the repository root, run the complete marked test suite with:

```bash
pytest module_4/tests -c module_4/pytest.ini -m "web or buttons or analysis or db or integration"
```

The completed test suite contains 102 passing tests and achieves 100% coverage of the code under `module_4/src`.

The successful coverage output is saved in:

```text
module_4/coverage_summary.txt
```

## GitHub Actions

Continuous integration is configured in:

```text
.github/workflows/tests.yml
```

The GitHub Actions workflow:

1. Checks out the repository.
2. Sets up Python 3.12.
3. Starts PostgreSQL.
4. Installs the project requirements.
5. Runs the complete marked Pytest suite.
6. Verifies the required 100% coverage.

A screenshot of the successful GitHub Actions run is included as:

```text
module_4/actions_success.png
```

## Sphinx Documentation

Sphinx source files are located in:

```text
module_4/docs/source/
```

The documentation includes:

- Overview and setup
- Application architecture
- API reference
- Testing guide

To build the documentation locally:

```bash
cd module_4/docs
make html
```

The generated HTML is placed in:

```text
module_4/docs/build/html/
```

## Published Documentation

The Sphinx documentation is published through Read the Docs:

https://lynn-jhu-software-concepts.readthedocs.io/en/latest/

## Module 4 Deliverables

The repository includes:

- Module 4 application source code
- Complete Pytest test suite
- 100% coverage summary
- GitHub Actions workflow
- Successful GitHub Actions screenshot
- Sphinx documentation
- Published Read the Docs documentation
- README
- Requirements file