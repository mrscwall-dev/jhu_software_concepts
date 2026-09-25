import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src import orm_queries
from src.models import Applicant, Base


TEST_DATABASE_URL = (
    "postgresql+psycopg://localhost/gradcafe_test"
)

test_engine = create_engine(
    TEST_DATABASE_URL
)

TestSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    expire_on_commit=False,
)


@pytest.fixture(autouse=True)
def reset_database(monkeypatch):
    Base.metadata.drop_all(test_engine)
    Base.metadata.create_all(test_engine)

    monkeypatch.setattr(
        orm_queries,
        "SessionLocal",
        TestSessionLocal,
    )

    yield

    Base.metadata.drop_all(test_engine)


@pytest.fixture
def sample_applicants():
    applicants = [
        Applicant(
            p_id=1,
            program=(
                "Computer Science, "
                "Stanford University"
            ),
            status="Accepted",
            term="Fall 2026",
            us_or_international="American",
            gpa=3.8,
            degree="PhD",
            llm_generated_program=(
                "Computer Science"
            ),
            llm_generated_university=(
                "Stanford University"
            ),
        ),
        Applicant(
            p_id=2,
            program=(
                "Data Science, "
                "Johns Hopkins University"
            ),
            status="Rejected",
            term="Fall 2026",
            us_or_international="American",
            gpa=4.0,
            degree="Masters",
            llm_generated_program=(
                "Data Science"
            ),
            llm_generated_university=(
                "Johns Hopkins University"
            ),
        ),
        Applicant(
            p_id=3,
            program="Computer Science, MIT",
            status="Accepted",
            term="Fall 2025",
            us_or_international="International",
            gpa=3.9,
            degree="PhD",
            llm_generated_program=(
                "Computer Science"
            ),
            llm_generated_university="MIT",
        ),
        Applicant(
            p_id=4,
            program=(
                "Computer Science, "
                "Carnegie Mellon University"
            ),
            status="Rejected",
            term="Fall 2025",
            us_or_international="American",
            gpa=3.7,
            degree="PhD",
            llm_generated_program=(
                "Computer Science"
            ),
            llm_generated_university=(
                "Carnegie Mellon University"
            ),
        ),
    ]

    with TestSessionLocal() as session:
        session.add_all(applicants)
        session.commit()


@pytest.mark.db
def test_question_1(sample_applicants):
    assert orm_queries.question_1() == 2


@pytest.mark.db
def test_question_4(sample_applicants):
    assert (
        orm_queries.question_4()
        == pytest.approx(3.9)
    )


@pytest.mark.db
def test_question_5(sample_applicants):
    assert (
        orm_queries.question_5()
        == pytest.approx(50.0)
    )


@pytest.mark.db
def test_question_8(sample_applicants):
    assert orm_queries.question_8() == 1


@pytest.mark.db
def test_question_9(sample_applicants):
    assert orm_queries.question_9() == 1


@pytest.mark.db
def test_question_10(sample_applicants):
    assert (
        orm_queries.question_10()
        == pytest.approx(50.0)
    )


@pytest.mark.db
def test_percentages_when_database_is_empty():
    assert orm_queries.question_5() == 0
    assert orm_queries.question_10() == 0


@pytest.mark.db
def test_main(monkeypatch, capsys):
    monkeypatch.setattr(
        orm_queries,
        "question_1",
        lambda: 10,
    )

    monkeypatch.setattr(
        orm_queries,
        "question_4",
        lambda: 3.79,
    )

    monkeypatch.setattr(
        orm_queries,
        "question_5",
        lambda: 47.92,
    )

    monkeypatch.setattr(
        orm_queries,
        "question_8",
        lambda: 28,
    )

    monkeypatch.setattr(
        orm_queries,
        "question_9",
        lambda: 30,
    )

    monkeypatch.setattr(
        orm_queries,
        "question_10",
        lambda: 37.10,
    )

    orm_queries.main()

    output = capsys.readouterr().out

    assert (
        "Fall 2026 applicant count: 10"
        in output
    )

    assert (
        "Original-field count: 28"
        in output
    )

    assert (
        "LLM-field count: 30"
        in output
    )

    assert "Difference: 2" in output
    assert "37.10%" in output