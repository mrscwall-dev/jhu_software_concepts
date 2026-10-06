# Module 5 - Software Assurance and Secure SQL

## Overview

This project builds on the Grad Café Analytics application developed in previous modules.

Module 5 focuses on software assurance and application security. The project adds Pylint static code analysis, SQL injection defenses, database security using environment variables and least-privilege access, dependency analysis with pydeps and Graphviz, Python packaging, Snyk dependency scanning, and expanded GitHub Actions continuous integration.

The application includes:

- A Flask Analysis webpage
- Pull Data and Update Analysis functionality
- PostgreSQL database storage
- Raw SQL and SQLAlchemy analysis queries
- Grad Café data processing
- Automated unit and integration tests
- 100% test coverage
- Pylint static code analysis
- SQL injection defenses
- Query LIMIT enforcement
- Environment-based database configuration
- Least-privilege database access
- Dependency analysis with pydeps and Graphviz
- Python package configuration with setup.py
- Snyk dependency security scanning
- GitHub Actions continuous integration
- Sphinx documentation

## Repository

GitHub repository:

```text
git@github.com:mrscwall-dev/jhu_software_concepts.git
```

## Project Structure

```text
module_5/
    src/                    Application source code
    tests/                  Pytest test suite
    docs/                   Sphinx documentation
    dependency.svg          Python dependency graph
    setup.py                Python package configuration
    pytest.ini              Pytest and coverage configuration
    requirements.txt        Python dependencies
    README.md               Module 5 project documentation
    .env.example            Example database environment variables
    coverage_summary.txt    Successful 100% coverage output
    snyk-analysis.png       Snyk dependency scan evidence
```

## Requirements

Python 3.12 is used for this project.

PostgreSQL must be installed and running.

Graphviz is required to generate the dependency graph.

The application uses a PostgreSQL database named:

```text
gradcafe
```

The automated database tests use:

```text
gradcafe_test
```

Database passwords and other credentials must not be committed to the repository.

## Fresh Install Using pip

From the `module_5` directory, create a virtual environment:

```bash
python3 -m venv .venv
```

Activate the virtual environment on macOS or Linux:

```bash
source .venv/bin/activate
```

Install the required dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Install the project as an editable package:

```bash
python3 -m pip install -e .
```

## Fresh Install Using uv

Create a virtual environment using uv:

```bash
uv venv
```

Activate the virtual environment on macOS or Linux:

```bash
source .venv/bin/activate
```

Synchronize the environment with the requirements file:

```bash
uv pip sync requirements.txt
```

Install the project as an editable package:

```bash
uv pip install -e .
```

## Database Environment Variables

Database connection information is loaded from environment variables rather than being hard-coded in the application.

The required variables are:

```text
DB_HOST
DB_PORT
DB_NAME
DB_USER
DB_PASSWORD
```

The `.env.example` file provides example variable names and placeholder values. Real passwords and other secrets must not be committed to version control.

Before running the application locally, set the database environment variables for your environment. For example:

```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=gradcafe
export DB_USER=your_database_user
export DB_PASSWORD=your_database_password
```

## Database Security

The application is designed to use a least-privilege PostgreSQL account.

The application database account is not a superuser and is not the owner of the database. It is granted only the database permissions required by the application.

SQL queries that use dynamic values use parameter binding rather than inserting user-supplied values directly into SQL text. Dynamic SQL identifiers are handled using psycopg SQL composition.

Query limits are also enforced to prevent oversized requests.

## Source Files

Application code is located under `module_5/src/`.

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

From the `module_5` folder, run:

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

From the `module_5` folder, run:

```bash
python3 -m src.load_data
```

The loader loads prepared applicant records into PostgreSQL.

Existing `p_id` values are not inserted again.

## Run Raw SQL Analysis

From the `module_5` folder, run:

```bash
python3 -m src.query_data
```

This executes the Grad Café analysis using raw SQL and psycopg.

## Run SQLAlchemy Analysis

From the `module_5` folder, run:

```bash
python3 -m src.orm_queries
```

This performs selected analyses using SQLAlchemy.

## Pull New Grad Café Data

From the `module_5` folder, run:

```bash
python3 -m src.pull_data
```

The Pull Data process checks for Grad Café records that are not already stored in PostgreSQL, processes the new records, and inserts new records into the database.

## Pylint

Run Pylint on all Python files under `src`:

```bash
pylint src
```

The Module 5 source code achieves the required:

```text
Your code has been rated at 10.00/10
```

## Automated Testing

Pytest tests are stored in:

```text
module_5/tests/
```

The required Pytest markers are:

- `web`
- `buttons`
- `analysis`
- `db`
- `integration`

Run the test suite from the `module_5` directory:

```bash
pytest
```

The completed test suite contains 104 passing tests and achieves 100% coverage of the code under `module_5/src`.

The successful coverage output is saved in:

```text
coverage_summary.txt
```

## Dependency Analysis

The Python dependency graph is generated using pydeps and Graphviz.

From the `module_5` directory, run:

```bash
pydeps src/app.py --noshow -T svg -o dependency.svg
```

The resulting dependency graph is saved as:

```text
dependency.svg
```

## Snyk Dependency Security Analysis

Snyk is used to scan project dependencies for known security vulnerabilities.

Run the dependency scan from the `module_5` directory:

```bash
snyk test
```

Evidence of the completed scan is saved as:

```text
snyk-analysis.png
```

## GitHub Actions

Continuous integration is configured under:

```text
.github/workflows/
```

The Module 5 GitHub Actions workflow performs the following security and quality checks:

1. Runs Pylint and enforces a minimum score of 10.
2. Generates and validates `dependency.svg` using pydeps and Graphviz.
3. Runs the Snyk dependency security scan.
4. Runs the Pytest test suite and verifies successful test completion.

A screenshot of the successful GitHub Actions run is included with the Module 5 deliverables.

## Sphinx Documentation

Sphinx source files are located in:

```text
module_5/docs/source/
```

To build the documentation locally:

```bash
cd docs
make html
```

The generated HTML is placed in:

```text
docs/build/html/
```

## Module 5 Deliverables

The Module 5 submission includes:

- Application source code
- Complete Pytest test suite
- 100% coverage summary
- Pylint 10.00/10 compliance
- Secure SQL query handling
- Query LIMIT enforcement
- Environment-based database configuration
- Least-privilege database configuration
- `dependency.svg`
- `setup.py`
- `requirements.txt`
- `.env.example`
- `snyk-analysis.png`
- GitHub Actions workflow
- Successful GitHub Actions screenshot
- Module 5 PDF report
- README
