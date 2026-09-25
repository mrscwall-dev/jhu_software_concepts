# Module 3 - Database Queries, SQLAlchemy, and Dynamic Webpages

## Overview

This project builds on the Grad Café data collected in Module 2. The cleaned applicant data is loaded into a PostgreSQL database and analyzed using both raw SQL and SQLAlchemy ORM queries. A Flask webpage dynamically displays the analysis results and provides options to retrieve newly available Grad Café records and refresh the analysis.

## Requirements

Install the required Python packages with:

```bash
python -m pip install -r requirements.txt
```

PostgreSQL must also be installed and running locally.

This project uses a PostgreSQL database named:

```text
gradcafe
```

The default database connection is:

```text
postgresql://localhost/gradcafe
```

Database passwords, API keys, and other credentials should not be stored in the repository.

## Project Files

- `load_data.py` - Creates the applicants table and loads the cleaned Module 2 data into PostgreSQL.
- `query_data.py` - Runs Questions 1-11 using raw SQL.
- `models.py` - Defines the SQLAlchemy Applicant model and database connection.
- `orm_queries.py` - Repeats selected analyses using SQLAlchemy ORM.
- `pull_data.py` - Checks Grad Café for newly available records, standardizes the new program and university information, and adds new records to PostgreSQL.
- `app.py` - Runs the Flask application.
- `templates/analysis.html` - Displays the dynamic analysis webpage.
- `static/style.css` - Provides styling for the webpage.
- `query_results.pdf` - Contains all 11 SQL questions, results, queries, and explanations.
- `limitations.pdf` - Discusses limitations of analyzing anonymous, self-reported Grad Café data.
- `raw_sql_output.png` - Screenshot of the raw SQL console output.
- `orm_output.png` - Screenshot of the SQLAlchemy ORM output.
- `flask_webpage.png` - Screenshot of the running Flask webpage.

## Load the Database

Make sure PostgreSQL is running and the `gradcafe` database exists.

Run:

```bash
python load_data.py
```

The loader creates the `applicants` table if needed and inserts the cleaned applicant records. Existing `p_id` values are not inserted again, which prevents unnecessary duplicate records.

## Run the Raw SQL Analysis

Run:

```bash
python query_data.py
```

This executes Questions 1-9 and the two original analysis questions using raw SQL through psycopg.

## Run the SQLAlchemy ORM Analysis

Run:

```bash
python orm_queries.py
```

This repeats Questions 1, 4, 5, 8, 9, and one original question using SQLAlchemy instead of handwritten SQL.

## Pull New Grad Café Data

Run:

```bash
python pull_data.py
```

The script checks Grad Café for records that are not already stored in PostgreSQL. New records are processed and added to the existing data without re-inserting records already in the database.

The new program and university information is also processed through the Module 2 LLM standardization step before the records are added to the database.

## Run the Flask Application

Run:

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5001
```

The webpage retrieves its analysis results dynamically from PostgreSQL using SQLAlchemy.

The **Pull Data** button starts the process of checking Grad Café for newly available records.

The **Update Analysis** button re-queries PostgreSQL and displays the most current analysis results without starting another scrape.

If Pull Data is already running, the application prevents another scraping process from starting and provides a status message to the user.

## Raw SQL vs. SQLAlchemy

For Question 1, I counted the number of applicants who applied for Fall 2026.

### Raw SQL

```sql
SELECT COUNT(*)
FROM applicants
WHERE LOWER(TRIM(term)) = 'fall 2026';
```

### SQLAlchemy

```python
statement = select(func.count()).select_from(Applicant).where(
    func.lower(func.trim(Applicant.term)) == "fall 2026"
)
```

Raw SQL is concise and makes it easy to see exactly what query is being sent to the database. It also gives the developer direct control over the database query. SQLAlchemy adds an abstraction layer that allows database operations to be written using Python objects and can make database code easier to integrate into a larger Python application. Both approaches produced the same result for this analysis, but each can be useful for different types of work.