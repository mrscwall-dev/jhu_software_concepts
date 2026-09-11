# Module 2 - Web Scraping Assignment

**Name:** Lynn Wall  
**JHED ID:** cbrook15  
**Module:** Module 2  
**Assignment:** Web Scraping and Local LLM Data Standardization  
**Due Date:** September 13, 2026

## Project Overview

This project collects publicly available graduate admissions data from The GradCafe, structures the data as JSON, and then uses a locally hosted language model to standardize program and university names.

The completed dataset contains 30,000 unique graduate applicant records.

## Project Files

- `scrape.py` - GradCafe scraping, parsing, pagination, duplicate prevention, incremental saving, and resume logic.
- `clean.py` - Prepares the scraped dataset for the provided local LLM standardizer.
- `applicant_data.json` - 30,000 scraped GradCafe applicant records.
- `llm_extend_applicant_data.json` - 30,000 records after local LLM standardization.
- `requirements.txt` - Python package requirements.
- `screenshot.jpg` - Evidence that GradCafe's robots.txt file was reviewed before scraping.
- `llm_hosting/` - Instructor-provided local LLM package, canonical lists, and related files.

## robots.txt Compliance

Before scraping GradCafe, I reviewed the site's `robots.txt` file.

The general `User-agent: *` rule allows access to `/`, while account-related paths including `/signin`, `/register`, `/forgot-password`, `/reset-password`, `/confirm-password`, `/verify-email`, and `/profile` are disallowed.

This project accessed only the publicly available GradCafe admissions results pages. It did not access login-protected or disallowed areas.

The scraper did not attempt to bypass Cloudflare, CAPTCHAs, login requirements, rate limits, or other access restrictions. Cloudflare verification was completed manually in a normal Chrome browser when required.

A screenshot of the reviewed robots.txt file is included as `screenshot.jpg`.

## Scraping Approach

A direct `urllib` or requests-style scrape returned HTTP 403 responses, and Selenium was not used in the final implementation because Cloudflare interfered with Selenium-controlled browser sessions.

The final solution used the hybrid browser-capture approach described in the course:

1. GradCafe was opened in a normal Chrome browser.
2. Cloudflare verification was completed manually when required.
3. Python communicated with the active Chrome page using macOS AppleScript.
4. The rendered HTML from the public admissions results page was captured.
5. BeautifulSoup, Python string methods, and regular expressions were used to extract applicant information.
6. `urllib.parse` utilities were used to construct, validate, join, and inspect GradCafe URLs.
7. The scraper followed the public `Next` pagination links and processed multiple results pages.
8. A delay was used between page changes to avoid rapid repeated access.
9. Data was saved incrementally so the process could resume instead of restarting after an interruption.
10. Applicant URLs were used to prevent duplicate records.

Raw HTML was used temporarily during development and processing but was not retained in the Git repository in order to keep the repository lightweight.

## Scraped Data

The final `applicant_data.json` contains 30,000 unique applicant records.

Fields include, when available:

- original/raw listing text
- original/raw program text
- program name
- university
- comments
- date added
- applicant URL
- applicant status
- decision date
- acceptance date
- rejection date
- semester and year of program start
- American / International / Other applicant type
- GRE score
- GRE verbal score
- GRE analytical writing score
- degree type
- GPA

Unavailable values are represented consistently with JSON `null` values generated from Python `None`.

The original program and listing information was preserved for traceability and reproducibility.

## Data Cleaning and Local LLM

The instructor-provided `llm_hosting` package was added under `module_2/llm_hosting`.

The package uses TinyLlama through `llama-cpp-python` to create two standardized values:

- `llm-generated-program`
- `llm-generated-university`

My scraped dataset stored the fields separately as `program_name` and `university`, while the provided LLM application expected an input field called `program`.

To make the supplied LLM package compatible with my dataset, `clean.py` creates a temporary `program` value containing the program and university information. This allows the instructor-provided application to process the records while preserving all original fields.

The LLM processing was tested on a small sample before processing the full dataset.

The 30,000 records were divided into four chunks of approximately 7,500 records and processed in parallel. The completed results were merged into:

`llm_extend_applicant_data.json`

The completed cleaned file contains 30,000 records with both `llm-generated-program` and `llm-generated-university` populated.

No changes were made to the provided canonical program or university lists.

## Cleaning Edge Cases and Limitations

The local LLM standardization is not expected to be perfect. Program and university names may contain unusual abbreviations, misspellings, uncommon institutions, applicant-entered wording, or combined program/university text.

The original values were preserved so future modules can compare standardized results against the source data.

The local LLM output should therefore be treated as a standardized first pass rather than a guaranteed authoritative correction.

## Python and Environment

The GradCafe scraper was developed with Python 3.14.

The instructor-provided `llama-cpp-python` requirement was run in a separate Python 3.12.10 virtual environment for compatibility.

The final scraping workflow uses Google Chrome and macOS AppleScript. This portion of the implementation is therefore macOS-specific.

## Installation

From the `module_2` folder:

```bash
python -m pip install -r requirements.txt