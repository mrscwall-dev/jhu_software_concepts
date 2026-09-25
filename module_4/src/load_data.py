import json
import os
import re
from datetime import datetime
from pathlib import Path

import psycopg


BASE_DIR = Path(__file__).resolve().parent
MODULE_DIR = BASE_DIR.parent

DATA_FILE = (
    MODULE_DIR
    / "llm_extend_applicant_data.json"
)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://localhost/gradcafe",
)


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS applicants (
    p_id INTEGER PRIMARY KEY,
    program TEXT,
    comments TEXT,
    date_added DATE,
    url TEXT,
    status TEXT,
    term TEXT,
    us_or_international TEXT,
    gpa DOUBLE PRECISION,
    gre DOUBLE PRECISION,
    gre_v DOUBLE PRECISION,
    gre_aw DOUBLE PRECISION,
    degree TEXT,
    llm_generated_program TEXT,
    llm_generated_university TEXT
);
"""


INSERT_SQL = """
INSERT INTO applicants (
    p_id,
    program,
    comments,
    date_added,
    url,
    status,
    term,
    us_or_international,
    gpa,
    gre,
    gre_v,
    gre_aw,
    degree,
    llm_generated_program,
    llm_generated_university
)
VALUES (
    %(p_id)s,
    %(program)s,
    %(comments)s,
    %(date_added)s,
    %(url)s,
    %(status)s,
    %(term)s,
    %(us_or_international)s,
    %(gpa)s,
    %(gre)s,
    %(gre_v)s,
    %(gre_aw)s,
    %(degree)s,
    %(llm_generated_program)s,
    %(llm_generated_university)s
)
ON CONFLICT (p_id) DO NOTHING;
"""


def get_p_id(url):
    """Get the numeric GradCafe result ID from the applicant URL."""

    if not url:
        return None

    match = re.search(
        r"/result/(\d+)",
        url,
    )

    if match:
        return int(match.group(1))

    return None


def parse_date(value):
    """Convert the GradCafe date into a PostgreSQL-compatible date."""

    if not value:
        return None

    return datetime.strptime(
        value,
        "%b %d, %Y",
    ).date()


def read_applicant_data():
    """Read the cleaned applicant data."""

    with DATA_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def prepare_record(applicant):
    """Map a cleaned applicant record to the database columns."""

    return {
        "p_id": get_p_id(
            applicant.get(
                "applicant_url"
            )
        ),
        "program": applicant.get(
            "program"
        ),
        "comments": applicant.get(
            "comments"
        ),
        "date_added": parse_date(
            applicant.get(
                "date_added"
            )
        ),
        "url": applicant.get(
            "applicant_url"
        ),
        "status": applicant.get(
            "status"
        ),
        "term": applicant.get(
            "program_start"
        ),
        "us_or_international": applicant.get(
            "applicant_type"
        ),
        "gpa": applicant.get(
            "gpa"
        ),
        "gre": applicant.get(
            "gre_score"
        ),
        "gre_v": applicant.get(
            "gre_verbal"
        ),
        "gre_aw": applicant.get(
            "gre_aw"
        ),
        "degree": applicant.get(
            "degree_type"
        ),
        "llm_generated_program": applicant.get(
            "llm-generated-program"
        ),
        "llm_generated_university": applicant.get(
            "llm-generated-university"
        ),
    }


def load_data():
    """Create the applicants table and load the cleaned applicant data."""

    try:
        applicants = read_applicant_data()
        inserted = 0
        skipped = 0

        with psycopg.connect(
            DATABASE_URL
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    CREATE_TABLE_SQL
                )

                for applicant in applicants:
                    record = prepare_record(
                        applicant
                    )

                    if (
                        record["p_id"]
                        is None
                    ):
                        skipped += 1
                        continue

                    cursor.execute(
                        INSERT_SQL,
                        record,
                    )

                    inserted += (
                        cursor.rowcount
                    )

        print(
            f"Applicant records read: "
            f"{len(applicants)}"
        )

        print(
            f"New records inserted: "
            f"{inserted}"
        )

        print(
            f"Records skipped: "
            f"{skipped}"
        )

    except FileNotFoundError:
        print(
            f"Data file not found: "
            f"{DATA_FILE}"
        )

    except psycopg.Error as error:
        print(
            f"Database error: "
            f"{error}"
        )


if __name__ == "__main__":  # pragma: no cover
    load_data()