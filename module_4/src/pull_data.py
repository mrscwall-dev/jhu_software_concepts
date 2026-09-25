import json
import os
import re
import subprocess
import time
from datetime import datetime
from pathlib import Path

from sqlalchemy import select

from src.models import Applicant, SessionLocal
from src.scrape import (
    GradCafeScraper,
    load_data as load_raw_data,
    merge_data,
    save_data as save_raw_data,
)


BASE_DIR = Path(__file__).resolve().parent
MODULE_DIR = BASE_DIR.parent

START_URL = "https://www.thegradcafe.com/survey"

EXTENDED_DATA_FILE = (
    MODULE_DIR / "llm_extend_applicant_data.json"
)


def get_p_id(url):
    """Extract the GradCafe result ID from an applicant URL."""

    if not url:
        return None

    match = re.search(r"/result/(\d+)", url)

    if match:
        return int(match.group(1))

    return None


def parse_date(value):
    """Convert a GradCafe date to a Python date."""

    if not value:
        return None

    try:
        return datetime.strptime(
            value,
            "%b %d, %Y",
        ).date()

    except ValueError:
        return None


def make_program(record):
    """Combine the original program and university fields."""

    program_name = record.get("program_name") or ""
    university = record.get("university") or ""

    combined = f"{program_name}, {university}".strip(", ")

    return combined or None


def open_gradcafe():
    """Open GradCafe in a separate Chrome window."""

    script = f'''
    tell application "Google Chrome"
        activate
        make new window
        set URL of active tab of front window to "{START_URL}"
    end tell
    '''

    subprocess.run(
        ["osascript", "-e", script],
        check=True,
    )

    time.sleep(2)


def get_existing_ids():
    """Return GradCafe IDs already stored in PostgreSQL."""

    with SessionLocal() as session:
        return set(
            session.scalars(
                select(Applicant.p_id)
            ).all()
        )


def collect_new_records():
    """Scrape newer entries until existing records are reached."""

    scraper = GradCafeScraper()
    existing_ids = get_existing_ids()

    if not existing_ids:
        raise RuntimeError(
            "The applicants table is empty. Run load_data.py first."
        )

    open_gradcafe()

    new_records = []
    seen_new_ids = set()
    page_number = 1

    while True:
        current_url, html = scraper.wait_for_results(
            timeout=120
        )

        records = scraper.scrape_data(html)

        found_existing = False

        for record in records:
            p_id = get_p_id(
                record.get("applicant_url")
            )

            if p_id is None:
                continue

            if p_id in existing_ids:
                found_existing = True
                continue

            if p_id not in seen_new_ids:
                new_records.append(record)
                seen_new_ids.add(p_id)

        print(
            f"Checked page {page_number}: "
            f"{len(records)} records found."
        )

        if found_existing:
            break

        next_url = scraper.get_next_url(html)

        if next_url is None:
            break

        time.sleep(4)
        scraper.navigate_to(next_url)
        page_number += 1

    return new_records


def standardize_new_records(new_records):
    """Run the Module 2 LLM standardizer over newly scraped records."""

    os.environ.setdefault(
        "CANON_UNIS_PATH",
        str(
            MODULE_DIR
            / "llm_hosting"
            / "canon_universities.txt"
        ),
    )

    os.environ.setdefault(
        "CANON_PROGS_PATH",
        str(
            MODULE_DIR
            / "llm_hosting"
            / "canon_programs.txt"
        ),
    )

    from module_4.llm_hosting.app import _call_llm

    standardized_records = []

    for record in new_records:
        extended_record = dict(record)

        extended_record["program"] = make_program(
            record
        )

        result = _call_llm(
            extended_record["program"] or ""
        )

        extended_record["llm-generated-program"] = (
            result["standardized_program"]
        )

        extended_record[
            "llm-generated-university"
        ] = result["standardized_university"]

        standardized_records.append(
            extended_record
        )

    return standardized_records


def update_raw_json(new_records):
    """Add new raw records to applicant_data.json."""

    existing_data = load_raw_data()

    added = merge_data(
        existing_data,
        new_records,
    )

    if added:
        save_raw_data(existing_data)

    return added


def update_extended_json(new_records):
    """Add standardized new records to the extended JSON file."""

    if EXTENDED_DATA_FILE.exists():
        with EXTENDED_DATA_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:
            existing = json.load(file)

    else:
        existing = []

    existing_urls = {
        record.get("applicant_url")
        for record in existing
        if record.get("applicant_url")
    }

    added = 0

    for record in new_records:
        url = record.get("applicant_url")

        if url and url not in existing_urls:
            existing.append(record)
            existing_urls.add(url)
            added += 1

    if added:
        with EXTENDED_DATA_FILE.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                existing,
                file,
                indent=2,
                ensure_ascii=False,
            )

    return added


def insert_into_database(records):
    """Insert standardized new records into PostgreSQL."""

    inserted = 0

    with SessionLocal() as session:
        for record in records:
            p_id = get_p_id(
                record.get("applicant_url")
            )

            if p_id is None:
                continue

            if (
                session.get(Applicant, p_id)
                is not None
            ):
                continue

            applicant = Applicant(
                p_id=p_id,
                program=record.get("program"),
                comments=record.get("comments"),
                date_added=parse_date(
                    record.get("date_added")
                ),
                url=record.get("applicant_url"),
                status=record.get("status"),
                term=record.get("program_start"),
                us_or_international=record.get(
                    "applicant_type"
                ),
                gpa=record.get("gpa"),
                gre=record.get("gre_score"),
                gre_v=record.get("gre_verbal"),
                gre_aw=record.get("gre_aw"),
                degree=record.get("degree_type"),
                llm_generated_program=record.get(
                    "llm-generated-program"
                ),
                llm_generated_university=record.get(
                    "llm-generated-university"
                ),
            )

            session.add(applicant)
            inserted += 1

        session.commit()

    return inserted


def pull_data():
    """Retrieve, standardize, and store newly available GradCafe records."""

    print("Checking GradCafe for new records...")

    new_records = collect_new_records()

    if not new_records:
        print(
            "No new GradCafe records were found."
        )
        return

    update_raw_json(new_records)

    standardized_records = (
        standardize_new_records(new_records)
    )

    update_extended_json(
        standardized_records
    )

    inserted = insert_into_database(
        standardized_records
    )

    print(
        f"New GradCafe records found: "
        f"{len(new_records)}"
    )

    print(
        f"New database records inserted: "
        f"{inserted}"
    )


if __name__ == "__main__":  # pragma: no cover
    pull_data()