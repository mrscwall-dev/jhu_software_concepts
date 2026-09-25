from sqlalchemy import func, or_, select

from src.models import Applicant, SessionLocal


def question_1():
    """Count applicants who applied for Fall 2026."""

    with SessionLocal() as session:
        statement = select(func.count()).select_from(Applicant).where(
            func.lower(func.trim(Applicant.term)) == "fall 2026"
        )
        return session.scalar(statement)


def question_4():
    """Calculate the average GPA of American Fall 2026 applicants."""

    with SessionLocal() as session:
        statement = select(func.avg(Applicant.gpa)).where(
            func.lower(func.trim(Applicant.term)) == "fall 2026",
            func.lower(func.trim(Applicant.us_or_international)) == "american",
            Applicant.gpa.is_not(None),
        )
        return session.scalar(statement)


def question_5():
    """Calculate the percentage of Fall 2025 entries that are acceptances."""

    with SessionLocal() as session:
        total_statement = select(func.count()).select_from(Applicant).where(
            func.lower(func.trim(Applicant.term)) == "fall 2025"
        )

        accepted_statement = select(func.count()).select_from(Applicant).where(
            func.lower(func.trim(Applicant.term)) == "fall 2025",
            func.lower(func.trim(Applicant.status)) == "accepted",
        )

        total = session.scalar(total_statement)
        accepted = session.scalar(accepted_statement)

        return (accepted / total) * 100 if total else 0


def question_8():
    """Count accepted Fall 2026 CS PhD applicants using original fields."""

    with SessionLocal() as session:
        statement = select(func.count()).select_from(Applicant).where(
            func.lower(func.trim(Applicant.term)) == "fall 2026",
            func.lower(func.trim(Applicant.status)) == "accepted",
            or_(
                func.lower(func.trim(Applicant.degree)).in_(
                    ["phd", "ph.d.", "ph.d"]
                ),
                func.lower(Applicant.degree).like("%doctor of philosophy%"),
            ),
            or_(
                func.lower(Applicant.program).like("%computer science%"),
                func.lower(Applicant.program).like("%comp sci%"),
                Applicant.program.op("~*")(r"(^|[^a-z])CS([^a-z]|$)"),
            ),
            or_(
                func.lower(Applicant.program).like("%georgetown%"),
                func.lower(Applicant.program).like(
                    "%massachusetts institute of technology%"
                ),
                Applicant.program.op("~*")(r"(^|[^a-z])MIT([^a-z]|$)"),
                func.lower(Applicant.program).like("%stanford%"),
                func.lower(Applicant.program).like("%carnegie mellon%"),
                Applicant.program.op("~*")(r"(^|[^a-z])CMU([^a-z]|$)"),
            ),
        )

        return session.scalar(statement)


def question_9():
    """Repeat Question 8 using LLM-generated program and university fields."""

    with SessionLocal() as session:
        statement = select(func.count()).select_from(Applicant).where(
            func.lower(func.trim(Applicant.term)) == "fall 2026",
            func.lower(func.trim(Applicant.status)) == "accepted",
            or_(
                func.lower(func.trim(Applicant.degree)).in_(
                    ["phd", "ph.d.", "ph.d"]
                ),
                func.lower(Applicant.degree).like("%doctor of philosophy%"),
            ),
            or_(
                func.lower(Applicant.llm_generated_program).like(
                    "%computer science%"
                ),
                func.lower(Applicant.llm_generated_program).like("%comp sci%"),
                Applicant.llm_generated_program.op("~*")(
                    r"(^|[^a-z])CS([^a-z]|$)"
                ),
            ),
            or_(
                func.lower(Applicant.llm_generated_university).like(
                    "%georgetown%"
                ),
                func.lower(Applicant.llm_generated_university).like(
                    "%massachusetts institute of technology%"
                ),
                Applicant.llm_generated_university.op("~*")(
                    r"(^|[^a-z])MIT([^a-z]|$)"
                ),
                func.lower(Applicant.llm_generated_university).like(
                    "%stanford%"
                ),
                func.lower(Applicant.llm_generated_university).like(
                    "%carnegie mellon%"
                ),
                Applicant.llm_generated_university.op("~*")(
                    r"(^|[^a-z])CMU([^a-z]|$)"
                ),
            ),
        )

        return session.scalar(statement)


def question_10():
    """Calculate the percentage of Fall 2026 entries that are acceptances."""

    with SessionLocal() as session:
        total_statement = select(func.count()).select_from(Applicant).where(
            func.lower(func.trim(Applicant.term)) == "fall 2026"
        )

        accepted_statement = select(func.count()).select_from(Applicant).where(
            func.lower(func.trim(Applicant.term)) == "fall 2026",
            func.lower(func.trim(Applicant.status)) == "accepted",
        )

        total = session.scalar(total_statement)
        accepted = session.scalar(accepted_statement)

        return (accepted / total) * 100 if total else 0


def main():
    """Print the query results."""

    original_count = question_8()
    llm_count = question_9()

    print(f"Question 1 - Fall 2026 applicant count: {question_1()}")
    print(
        "Question 4 - Average GPA of American Fall 2026 applicants: "
        f"{question_4():.2f}"
    )
    print(
        "Question 5 - Fall 2025 acceptance percentage: "
        f"{question_5():.2f}%"
    )
    print(f"Question 8 - Original-field count: {original_count}")
    print(f"Question 9 - LLM-field count: {llm_count}")
    print(f"Question 9 - Difference: {llm_count - original_count}")
    print(
        "Question 10 - Fall 2026 acceptance percentage: "
        f"{question_10():.2f}%"
    )


if __name__ == "__main__":  # pragma: no cover
    main()