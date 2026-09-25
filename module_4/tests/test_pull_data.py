import json
import sys
import types
from datetime import date

import pytest

from src import pull_data


@pytest.mark.db
def test_get_p_id():
    assert (
        pull_data.get_p_id(
            "https://www.thegradcafe.com/result/12345"
        )
        == 12345
    )

    assert pull_data.get_p_id("") is None

    assert (
        pull_data.get_p_id(
            "https://www.thegradcafe.com/survey"
        )
        is None
    )


@pytest.mark.db
def test_parse_date():
    assert (
        pull_data.parse_date("Sep 24, 2026")
        == date(2026, 9, 24)
    )

    assert pull_data.parse_date("") is None
    assert pull_data.parse_date("bad date") is None


@pytest.mark.db
def test_make_program():
    record = {
        "program_name": "Computer Science",
        "university": "Johns Hopkins University",
    }

    assert pull_data.make_program(record) == (
        "Computer Science, Johns Hopkins University"
    )

    assert pull_data.make_program({}) is None


@pytest.mark.db
def test_open_gradcafe(monkeypatch):
    calls = []

    def fake_run(command, check):
        calls.append(command)

    monkeypatch.setattr(
        pull_data.subprocess,
        "run",
        fake_run,
    )

    monkeypatch.setattr(
        pull_data.time,
        "sleep",
        lambda seconds: None,
    )

    pull_data.open_gradcafe()

    assert calls
    assert calls[0][0] == "osascript"


@pytest.mark.db
def test_get_existing_ids(monkeypatch):
    class FakeScalarResult:
        def all(self):
            return [100, 101, 102]

    class FakeSession:
        def __enter__(self):
            return self

        def __exit__(
            self,
            exc_type,
            exc_value,
            traceback,
        ):
            return False

        def scalars(self, statement):
            return FakeScalarResult()

    monkeypatch.setattr(
        pull_data,
        "SessionLocal",
        lambda: FakeSession(),
    )

    result = pull_data.get_existing_ids()

    assert result == {100, 101, 102}


@pytest.mark.db
def test_collect_new_records(monkeypatch):
    monkeypatch.setattr(
        pull_data,
        "get_existing_ids",
        lambda: {100},
    )

    monkeypatch.setattr(
        pull_data,
        "open_gradcafe",
        lambda: None,
    )

    class FakeScraper:
        def wait_for_results(self, timeout):
            return "test-url", "test-html"

        def scrape_data(self, html):
            return [
                {
                    "applicant_url": (
                        "https://www.thegradcafe.com/result/101"
                    )
                },
                {
                    "applicant_url": (
                        "https://www.thegradcafe.com/result/100"
                    )
                },
                {
                    "applicant_url": ""
                },
            ]

        def get_next_url(self, html):
            return None

        def navigate_to(self, url):
            return None

    monkeypatch.setattr(
        pull_data,
        "GradCafeScraper",
        FakeScraper,
    )

    result = pull_data.collect_new_records()

    assert len(result) == 1

    assert (
        result[0]["applicant_url"]
        == "https://www.thegradcafe.com/result/101"
    )


@pytest.mark.db
def test_collect_new_records_multiple_pages(
    monkeypatch,
):
    monkeypatch.setattr(
        pull_data,
        "get_existing_ids",
        lambda: {100},
    )

    monkeypatch.setattr(
        pull_data,
        "open_gradcafe",
        lambda: None,
    )

    monkeypatch.setattr(
        pull_data.time,
        "sleep",
        lambda seconds: None,
    )

    navigated = []

    class FakeScraper:
        def __init__(self):
            self.page = 0

        def wait_for_results(self, timeout):
            self.page += 1

            return (
                f"test-url-{self.page}",
                f"test-html-{self.page}",
            )

        def scrape_data(self, html):
            if self.page == 1:
                return [
                    {
                        "applicant_url": (
                            "https://www.thegradcafe.com/result/101"
                        )
                    }
                ]

            return [
                {
                    "applicant_url": (
                        "https://www.thegradcafe.com/result/100"
                    )
                }
            ]

        def get_next_url(self, html):
            return (
                "https://www.thegradcafe.com/survey?page=2"
            )

        def navigate_to(self, url):
            navigated.append(url)

    monkeypatch.setattr(
        pull_data,
        "GradCafeScraper",
        FakeScraper,
    )

    result = pull_data.collect_new_records()

    assert len(result) == 1

    assert navigated == [
        "https://www.thegradcafe.com/survey?page=2"
    ]


@pytest.mark.db
def test_collect_new_records_empty_database(
    monkeypatch,
):
    monkeypatch.setattr(
        pull_data,
        "get_existing_ids",
        lambda: set(),
    )

    with pytest.raises(RuntimeError):
        pull_data.collect_new_records()


@pytest.mark.db
def test_standardize_new_records(monkeypatch):
    fake_module = types.ModuleType(
        "module_4.llm_hosting.app"
    )

    def fake_call_llm(program):
        return {
            "standardized_program": (
                "Computer Science"
            ),
            "standardized_university": (
                "Johns Hopkins University"
            ),
        }

    fake_module._call_llm = fake_call_llm

    monkeypatch.setitem(
        sys.modules,
        "module_4.llm_hosting.app",
        fake_module,
    )

    records = [
        {
            "program_name": "Computer Science",
            "university": "Johns Hopkins University",
        }
    ]

    result = pull_data.standardize_new_records(
        records
    )

    assert len(result) == 1

    assert result[0]["program"] == (
        "Computer Science, Johns Hopkins University"
    )

    assert (
        result[0]["llm-generated-program"]
        == "Computer Science"
    )

    assert (
        result[0]["llm-generated-university"]
        == "Johns Hopkins University"
    )


@pytest.mark.db
def test_update_raw_json(monkeypatch):
    existing_data = [
        {
            "applicant_url": "old"
        }
    ]

    monkeypatch.setattr(
        pull_data,
        "load_raw_data",
        lambda: existing_data,
    )

    monkeypatch.setattr(
        pull_data,
        "merge_data",
        lambda existing, new: 1,
    )

    saved = []

    monkeypatch.setattr(
        pull_data,
        "save_raw_data",
        lambda data: saved.append(data),
    )

    result = pull_data.update_raw_json(
        [
            {
                "applicant_url": "new"
            }
        ]
    )

    assert result == 1
    assert saved == [existing_data]


@pytest.mark.db
def test_update_extended_json(
    tmp_path,
    monkeypatch,
):
    test_file = tmp_path / "extended.json"

    existing = [
        {
            "applicant_url": (
                "https://www.thegradcafe.com/result/1"
            )
        }
    ]

    with test_file.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(existing, file)

    monkeypatch.setattr(
        pull_data,
        "EXTENDED_DATA_FILE",
        test_file,
    )

    new_records = [
        {
            "applicant_url": (
                "https://www.thegradcafe.com/result/1"
            )
        },
        {
            "applicant_url": (
                "https://www.thegradcafe.com/result/2"
            )
        },
    ]

    added = pull_data.update_extended_json(
        new_records
    )

    assert added == 1

    with test_file.open(
        "r",
        encoding="utf-8",
    ) as file:
        saved = json.load(file)

    assert len(saved) == 2


@pytest.mark.db
def test_update_extended_json_new_file(
    tmp_path,
    monkeypatch,
):
    test_file = tmp_path / "new_extended.json"

    monkeypatch.setattr(
        pull_data,
        "EXTENDED_DATA_FILE",
        test_file,
    )

    records = [
        {
            "applicant_url": (
                "https://www.thegradcafe.com/result/10"
            )
        }
    ]

    added = pull_data.update_extended_json(
        records
    )

    assert added == 1
    assert test_file.exists()

    with test_file.open(
        "r",
        encoding="utf-8",
    ) as file:
        saved = json.load(file)

    assert saved == records


@pytest.mark.db
def test_insert_into_database(monkeypatch):
    added_records = []
    committed = {"value": False}

    class FakeSession:
        def __enter__(self):
            return self

        def __exit__(
            self,
            exc_type,
            exc_value,
            traceback,
        ):
            return False

        def get(self, model, p_id):
            if p_id == 200:
                return object()

            return None

        def add(self, applicant):
            added_records.append(applicant)

        def commit(self):
            committed["value"] = True

    monkeypatch.setattr(
        pull_data,
        "SessionLocal",
        lambda: FakeSession(),
    )

    records = [
        {
            "applicant_url": "",
        },
        {
            "applicant_url": (
                "https://www.thegradcafe.com/result/200"
            ),
        },
        {
            "applicant_url": (
                "https://www.thegradcafe.com/result/201"
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
            "llm-generated-program": (
                "Computer Science"
            ),
            "llm-generated-university": (
                "Johns Hopkins University"
            ),
        },
    ]

    inserted = pull_data.insert_into_database(
        records
    )

    assert inserted == 1
    assert len(added_records) == 1
    assert added_records[0].p_id == 201
    assert added_records[0].program == (
        "Computer Science"
    )
    assert committed["value"] is True


@pytest.mark.db
def test_pull_data_no_new_records(
    monkeypatch,
    capsys,
):
    monkeypatch.setattr(
        pull_data,
        "collect_new_records",
        lambda: [],
    )

    pull_data.pull_data()

    output = capsys.readouterr().out

    assert (
        "No new GradCafe records were found."
        in output
    )


@pytest.mark.db
def test_pull_data_success(
    monkeypatch,
    capsys,
):
    new_records = [
        {
            "applicant_url": (
                "https://www.thegradcafe.com/result/123"
            )
        }
    ]

    standardized = [
        {
            "applicant_url": (
                "https://www.thegradcafe.com/result/123"
            ),
            "program": "Computer Science",
        }
    ]

    monkeypatch.setattr(
        pull_data,
        "collect_new_records",
        lambda: new_records,
    )

    monkeypatch.setattr(
        pull_data,
        "update_raw_json",
        lambda records: 1,
    )

    monkeypatch.setattr(
        pull_data,
        "standardize_new_records",
        lambda records: standardized,
    )

    monkeypatch.setattr(
        pull_data,
        "update_extended_json",
        lambda records: 1,
    )

    monkeypatch.setattr(
        pull_data,
        "insert_into_database",
        lambda records: 1,
    )

    pull_data.pull_data()

    output = capsys.readouterr().out

    assert (
        "New GradCafe records found: 1"
        in output
    )

    assert (
        "New database records inserted: 1"
        in output
    )