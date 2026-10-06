import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker

from src.app import create_app
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
            "p_id": 910001,
            "program": "Computer Science, Johns Hopkins University",
            "comments": "Integration test one",
            "date_added": None,
            "url": "https://www.thegradcafe.com/result/910001",
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
            "p_id": 910002,
            "program": "Computer Science, Stanford University",
            "comments": "Integration test two",
            "date_added": None,
            "url": "https://www.thegradcafe.com/result/910002",
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


def fake_query():
    with TestSessionLocal() as session:
        total = session.scalar(
            select(func.count()).select_from(Applicant)
        )

    return {
        "q1": total,
        "q2": 50.00,
        "gpa": 3.85,
        "gre": 164.00,
        "gre_v": 159.50,
        "gre_aw": 4.25,
        "q4": 3.80,
        "q5": 50.00,
        "q6": 3.85,
        "q7": 1,
        "q8": 1,
        "q9": 1,
        "difference": 0,
        "q10": 100.00,
        "q11": 3.90,
    }


@pytest.mark.integration
def test_pull_update_render():
    app = create_app(
        {"TESTING": True},
        scraper=fake_scraper,
        loader=fake_loader,
        query_func=fake_query,
    )

    client = app.test_client()

    pull_response = client.post("/pull-data")

    assert pull_response.status_code == 200
    assert pull_response.get_json() == {"ok": True}

    with TestSessionLocal() as session:
        rows = session.scalars(select(Applicant)).all()

    assert len(rows) == 2

    update_response = client.post("/update-analysis")

    assert update_response.status_code == 200
    assert update_response.get_json() == {"ok": True}

    page_response = client.get("/analysis")
    page = page_response.get_data(as_text=True)

    assert page_response.status_code == 200
    assert "Answer:" in page
    assert "50.00%" in page
    assert "100.00%" in page


@pytest.mark.integration
def test_multiple_pulls_do_not_duplicate_rows():
    app = create_app(
        {"TESTING": True},
        scraper=fake_scraper,
        loader=fake_loader,
        query_func=fake_query,
    )

    client = app.test_client()

    first_response = client.post("/pull-data")
    second_response = client.post("/pull-data")

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    with TestSessionLocal() as session:
        rows = session.scalars(select(Applicant)).all()

    assert len(rows) == 2