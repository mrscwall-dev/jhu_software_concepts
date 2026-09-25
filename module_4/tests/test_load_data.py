import json
from datetime import date

import psycopg
import pytest

from src import load_data


@pytest.mark.db
def test_get_p_id():
    assert (
        load_data.get_p_id(
            "https://www.thegradcafe.com/result/12345"
        )
        == 12345
    )

    assert load_data.get_p_id("") is None

    assert (
        load_data.get_p_id(
            "https://www.thegradcafe.com/survey"
        )
        is None
    )


@pytest.mark.db
def test_parse_date():
    assert (
        load_data.parse_date("Sep 24, 2026")
        == date(2026, 9, 24)
    )

    assert load_data.parse_date("") is None


@pytest.mark.db
def test_read_applicant_data(tmp_path, monkeypatch):
    test_file = tmp_path / "applicants.json"

    test_data = [
        {
            "program": "Computer Science",
            "status": "Accepted",
        }
    ]

    with test_file.open("w", encoding="utf-8") as file:
        json.dump(test_data, file)

    monkeypatch.setattr(
        load_data,
        "DATA_FILE",
        test_file,
    )

    result = load_data.read_applicant_data()

    assert result == test_data


@pytest.mark.db
def test_prepare_record():
    applicant = {
        "applicant_url": (
            "https://www.thegradcafe.com/result/12345"
        ),
        "program": "Computer Science",
        "comments": "Test comment",
        "date_added": "Sep 24, 2026",
        "status": "Accepted",
        "program_start": "Fall 2026",
        "applicant_type": "International",
        "gpa": 3.9,
        "gre_score": 165,
        "gre_verbal": 160,
        "gre_aw": 4.5,
        "degree_type": "Masters",
        "llm-generated-program": "Computer Science",
        "llm-generated-university": (
            "Johns Hopkins University"
        ),
    }

    result = load_data.prepare_record(applicant)

    assert result["p_id"] == 12345
    assert result["program"] == "Computer Science"
    assert result["status"] == "Accepted"
    assert result["term"] == "Fall 2026"
    assert result["gpa"] == 3.9
    assert result["degree"] == "Masters"


@pytest.mark.db
def test_load_data_success(monkeypatch, capsys):
    applicants = [
        {
            "applicant_url": (
                "https://www.thegradcafe.com/result/10001"
            ),
            "program": "Computer Science",
            "comments": "Test record",
            "date_added": "Sep 24, 2026",
            "status": "Accepted",
            "program_start": "Fall 2026",
            "applicant_type": "International",
            "gpa": 3.9,
            "gre_score": 165,
            "gre_verbal": 160,
            "gre_aw": 4.5,
            "degree_type": "Masters",
            "llm-generated-program": "Computer Science",
            "llm-generated-university": (
                "Johns Hopkins University"
            ),
        },
        {
            "applicant_url": "",
            "program": "Data Science",
        },
    ]

    monkeypatch.setattr(
        load_data,
        "read_applicant_data",
        lambda: applicants,
    )

    class FakeCursor:
        def __init__(self):
            self.rowcount = 1

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return False

        def execute(self, sql, record=None):
            return None

    class FakeConnection:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return False

        def cursor(self):
            return FakeCursor()

    monkeypatch.setattr(
        load_data.psycopg,
        "connect",
        lambda database_url: FakeConnection(),
    )

    load_data.load_data()

    output = capsys.readouterr().out

    assert "Applicant records read: 2" in output
    assert "New records inserted: 1" in output
    assert "Records skipped: 1" in output


@pytest.mark.db
def test_load_data_file_not_found(monkeypatch, capsys):
    def fake_read():
        raise FileNotFoundError

    monkeypatch.setattr(
        load_data,
        "read_applicant_data",
        fake_read,
    )

    load_data.load_data()

    output = capsys.readouterr().out

    assert "Data file not found:" in output


@pytest.mark.db
def test_load_data_database_error(monkeypatch, capsys):
    monkeypatch.setattr(
        load_data,
        "read_applicant_data",
        lambda: [],
    )

    def fake_connect(database_url):
        raise psycopg.Error("Test database error")

    monkeypatch.setattr(
        load_data.psycopg,
        "connect",
        fake_connect,
    )

    load_data.load_data()

    output = capsys.readouterr().out

    assert "Database error:" in output