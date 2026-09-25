import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from src.app import create_app, get_analysis_results
from src.models import Applicant, Base


TEST_DATABASE_URL = "postgresql+psycopg://localhost/gradcafe_test"

test_engine = create_engine(TEST_DATABASE_URL)

TestSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    expire_on_commit=False,
)


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(test_engine)
    Base.metadata.create_all(test_engine)

    yield

    Base.metadata.drop_all(test_engine)


def fake_scraper():
    return [
        {
            "p_id": 900001,
            "program": "Computer Science, Johns Hopkins University",
            "comments": "Test record one",
            "date_added": None,
            "url": "https://www.thegradcafe.com/result/900001",
            "status": "Accepted",
            "term": "Fall 2026",
            "us_or_international": "International",
            "gpa": 3.90,
            "gre": 165.0,
            "gre_v": 160.0,
            "gre_aw": 4.5,
            "degree": "Masters",
            "llm_generated_program": "Computer Science",
            "llm_generated_university": "Johns Hopkins University",
        },
        {
            "p_id": 900002,
            "program": "Computer Science, Stanford University",
            "comments": "Test record two",
            "date_added": None,
            "url": "https://www.thegradcafe.com/result/900002",
            "status": "Accepted",
            "term": "Fall 2026",
            "us_or_international": "American",
            "gpa": 3.80,
            "gre": 163.0,
            "gre_v": 159.0,
            "gre_aw": 4.0,
            "degree": "PhD",
            "llm_generated_program": "Computer Science",
            "llm_generated_university": "Stanford University",
        },
    ]


def fake_loader(rows):
    with TestSessionLocal() as session:
        for row in rows:
            if session.get(Applicant, row["p_id"]) is None:
                session.add(Applicant(**row))

        session.commit()


@pytest.mark.db
def test_insert_on_pull():
    with TestSessionLocal() as session:
        before = session.scalars(select(Applicant)).all()

    assert before == []

    app = create_app(
        {"TESTING": True},
        scraper=fake_scraper,
        loader=fake_loader,
    )

    client = app.test_client()

    response = client.post("/pull-data")

    assert response.status_code == 200
    assert response.get_json() == {"ok": True}

    with TestSessionLocal() as session:
        rows = session.scalars(select(Applicant)).all()

    assert len(rows) == 2

    for row in rows:
        assert row.p_id is not None
        assert row.program is not None
        assert row.url is not None
        assert row.status is not None
        assert row.term is not None


@pytest.mark.db
def test_duplicate_pull_does_not_duplicate_rows():
    app = create_app(
        {"TESTING": True},
        scraper=fake_scraper,
        loader=fake_loader,
    )

    client = app.test_client()

    first_response = client.post("/pull-data")
    second_response = client.post("/pull-data")

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    with TestSessionLocal() as session:
        rows = session.scalars(select(Applicant)).all()

    assert len(rows) == 2


@pytest.mark.db
def test_query_returns_expected_keys(monkeypatch):
    fake_loader(fake_scraper())

    monkeypatch.setattr(
        "src.app.SessionLocal",
        TestSessionLocal,
    )

    monkeypatch.setattr(
        "src.app.question_1",
        lambda: 2,
    )

    monkeypatch.setattr(
        "src.app.question_4",
        lambda: 3.80,
    )

    monkeypatch.setattr(
        "src.app.question_5",
        lambda: 50.00,
    )

    monkeypatch.setattr(
        "src.app.question_8",
        lambda: 1,
    )

    monkeypatch.setattr(
        "src.app.question_9",
        lambda: 1,
    )

    monkeypatch.setattr(
        "src.app.question_10",
        lambda: 100.00,
    )

    results = get_analysis_results()

    expected_keys = {
        "q1",
        "q2",
        "gpa",
        "gre",
        "gre_v",
        "gre_aw",
        "q4",
        "q5",
        "q6",
        "q7",
        "q8",
        "q9",
        "difference",
        "q10",
        "q11",
    }

    assert set(results.keys()) == expected_keys