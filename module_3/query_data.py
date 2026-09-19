import os

import psycopg


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://localhost/gradcafe",
)


def question_1():
    """Count applicants who applied for Fall 2026."""

    sql = """
    SELECT COUNT(*)
    FROM applicants
    WHERE LOWER(TRIM(term)) = 'fall 2026';
    """

    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchone()[0]

    print(f"Fall 2026 applicant count: {result}")


def question_2():
    """Calculate the percentage of classified applicants who are international."""

    sql = """
    SELECT
        100.0 * COUNT(*) FILTER (
            WHERE LOWER(TRIM(us_or_international)) = 'international'
        ) / NULLIF(COUNT(*), 0)
    FROM applicants
    WHERE us_or_international IS NOT NULL
      AND TRIM(us_or_international) <> '';
    """

    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchone()[0]

    print(f"Percent international: {result:.2f}%")


def question_3():
    """Calculate average GPA and GRE scores separately."""

    sql = """
    SELECT
        AVG(gpa),
        AVG(gre),
        AVG(gre_v),
        AVG(gre_aw)
    FROM applicants;
    """

    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            gpa, gre, gre_v, gre_aw = cursor.fetchone()

    print(f"Average GPA: {gpa:.2f}")
    print(f"Average GRE Quantitative: {gre:.2f}")
    print(f"Average GRE Verbal: {gre_v:.2f}")
    print(f"Average GRE Analytical Writing: {gre_aw:.2f}")


def question_4():
    """Calculate the average GPA of American Fall 2026 applicants."""

    sql = """
    SELECT AVG(gpa)
    FROM applicants
    WHERE LOWER(TRIM(term)) = 'fall 2026'
      AND LOWER(TRIM(us_or_international)) = 'american'
      AND gpa IS NOT NULL;
    """

    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchone()[0]

    print(f"Average GPA of American Fall 2026 applicants: {result:.2f}")


def question_5():
    """Calculate the percentage of Fall 2025 entries that are acceptances."""

    sql = """
    SELECT
        100.0 * COUNT(*) FILTER (
            WHERE LOWER(TRIM(status)) = 'accepted'
        ) / NULLIF(COUNT(*), 0)
    FROM applicants
    WHERE LOWER(TRIM(term)) = 'fall 2025';
    """

    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchone()[0]

    print(f"Fall 2025 acceptance percentage: {result:.2f}%")


def question_6():
    """Calculate the average GPA of accepted Fall 2026 applicants."""

    sql = """
    SELECT AVG(gpa)
    FROM applicants
    WHERE LOWER(TRIM(term)) = 'fall 2026'
      AND LOWER(TRIM(status)) = 'accepted'
      AND gpa IS NOT NULL;
    """

    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchone()[0]

    print(f"Average GPA of accepted Fall 2026 applicants: {result:.2f}")


def question_7():
    """Count master's applicants in Computer Science at Johns Hopkins."""

    sql = """
    SELECT COUNT(*)
    FROM applicants
    WHERE (
        LOWER(program) LIKE '%johns hopkins%'
        OR program ~* '(^|[^a-z])JHU([^a-z]|$)'
    )
      AND (
        LOWER(program) LIKE '%computer science%'
        OR program ~* '(^|[^a-z])CS([^a-z]|$)'
    )
      AND (
        LOWER(TRIM(degree)) LIKE 'master%'
        OR LOWER(TRIM(degree)) IN ('ms', 'm.s.')
    );
    """

    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchone()[0]

    print(f"Johns Hopkins master's Computer Science applicant count: {result}")


def question_8():
    """Count accepted Fall 2026 CS PhD applicants using original fields."""

    sql = """
    SELECT COUNT(*)
    FROM applicants
    WHERE LOWER(TRIM(term)) = 'fall 2026'
      AND LOWER(TRIM(status)) = 'accepted'
      AND (
          LOWER(TRIM(degree)) IN ('phd', 'ph.d.', 'ph.d')
          OR LOWER(degree) LIKE '%doctor of philosophy%'
      )
      AND (
          LOWER(program) LIKE '%computer science%'
          OR LOWER(program) LIKE '%comp sci%'
          OR program ~* '(^|[^a-z])CS([^a-z]|$)'
      )
      AND (
          LOWER(program) LIKE '%georgetown%'
          OR LOWER(program) LIKE '%massachusetts institute of technology%'
          OR program ~* '(^|[^a-z])MIT([^a-z]|$)'
          OR LOWER(program) LIKE '%stanford%'
          OR LOWER(program) LIKE '%carnegie mellon%'
          OR program ~* '(^|[^a-z])CMU([^a-z]|$)'
      );
    """

    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchone()[0]

    return result


def question_9():
    """Repeat Question 8 using LLM-generated program and university fields."""

    sql = """
    SELECT COUNT(*)
    FROM applicants
    WHERE LOWER(TRIM(term)) = 'fall 2026'
      AND LOWER(TRIM(status)) = 'accepted'
      AND (
          LOWER(TRIM(degree)) IN ('phd', 'ph.d.', 'ph.d')
          OR LOWER(degree) LIKE '%doctor of philosophy%'
      )
      AND (
          LOWER(llm_generated_program) LIKE '%computer science%'
          OR LOWER(llm_generated_program) LIKE '%comp sci%'
          OR llm_generated_program ~* '(^|[^a-z])CS([^a-z]|$)'
      )
      AND (
          LOWER(llm_generated_university) LIKE '%georgetown%'
          OR LOWER(llm_generated_university) LIKE '%massachusetts institute of technology%'
          OR llm_generated_university ~* '(^|[^a-z])MIT([^a-z]|$)'
          OR LOWER(llm_generated_university) LIKE '%stanford%'
          OR LOWER(llm_generated_university) LIKE '%carnegie mellon%'
          OR llm_generated_university ~* '(^|[^a-z])CMU([^a-z]|$)'
      );
    """

    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchone()[0]

    return result


def question_10():
    """Calculate the percentage of Fall 2026 entries that are acceptances."""

    sql = """
    SELECT
        100.0 * COUNT(*) FILTER (
            WHERE LOWER(TRIM(status)) = 'accepted'
        ) / NULLIF(COUNT(*), 0)
    FROM applicants
    WHERE LOWER(TRIM(term)) = 'fall 2026';
    """

    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchone()[0]

    print(f"Fall 2026 acceptance percentage: {result:.2f}%")


def question_11():
    """Calculate the average GPA of international Fall 2026 applicants."""

    sql = """
    SELECT AVG(gpa)
    FROM applicants
    WHERE LOWER(TRIM(term)) = 'fall 2026'
      AND LOWER(TRIM(us_or_international)) = 'international'
      AND gpa IS NOT NULL;
    """

    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchone()[0]

    print(f"Average GPA of international Fall 2026 applicants: {result:.2f}")


if __name__ == "__main__":
    question_1()
    question_2()
    question_3()
    question_4()
    question_5()
    question_6()
    question_7()

    original_count = question_8()
    llm_count = question_9()
    difference = llm_count - original_count

    print(f"Original-field count: {original_count}")
    print(f"LLM-field count: {llm_count}")
    print(f"Difference: {difference}")

    question_10()
    question_11()