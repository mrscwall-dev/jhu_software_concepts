import pytest

from src import query_data


class FakeCursor:
    def __init__(self, result):
        self.result = result

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def execute(self, sql):
        return None

    def fetchone(self):
        return self.result


class FakeConnection:
    def __init__(self, result):
        self.result = result

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def cursor(self):
        return FakeCursor(self.result)


def set_fake_result(monkeypatch, result):
    monkeypatch.setattr(
        query_data.psycopg,
        "connect",
        lambda database_url: FakeConnection(result),
    )


@pytest.mark.db
def test_question_1(monkeypatch, capsys):
    set_fake_result(monkeypatch, (25,))

    query_data.question_1()

    output = capsys.readouterr().out

    assert "Fall 2026 applicant count: 25" in output


@pytest.mark.db
def test_question_2(monkeypatch, capsys):
    set_fake_result(monkeypatch, (46.29,))

    query_data.question_2()

    output = capsys.readouterr().out

    assert "Percent international: 46.29%" in output


@pytest.mark.db
def test_question_3(monkeypatch, capsys):
    set_fake_result(
        monkeypatch,
        (3.85, 262.93, 161.53, 8.34),
    )

    query_data.question_3()

    output = capsys.readouterr().out

    assert "Average GPA: 3.85" in output
    assert "Average GRE Quantitative: 262.93" in output
    assert "Average GRE Verbal: 161.53" in output
    assert "Average GRE Analytical Writing: 8.34" in output


@pytest.mark.db
def test_question_4(monkeypatch, capsys):
    set_fake_result(monkeypatch, (3.79,))

    query_data.question_4()

    output = capsys.readouterr().out

    assert (
        "Average GPA of American Fall 2026 applicants: 3.79"
        in output
    )


@pytest.mark.db
def test_question_5(monkeypatch, capsys):
    set_fake_result(monkeypatch, (47.92,))

    query_data.question_5()

    output = capsys.readouterr().out

    assert "Fall 2025 acceptance percentage: 47.92%" in output


@pytest.mark.db
def test_question_6(monkeypatch, capsys):
    set_fake_result(monkeypatch, (3.88,))

    query_data.question_6()

    output = capsys.readouterr().out

    assert (
        "Average GPA of accepted Fall 2026 applicants: 3.88"
        in output
    )


@pytest.mark.db
def test_question_7(monkeypatch, capsys):
    set_fake_result(monkeypatch, (8,))

    query_data.question_7()

    output = capsys.readouterr().out

    assert (
        "Johns Hopkins master's Computer Science applicant count: 8"
        in output
    )


@pytest.mark.db
def test_question_8(monkeypatch):
    set_fake_result(monkeypatch, (28,))

    result = query_data.question_8()

    assert result == 28


@pytest.mark.db
def test_question_9(monkeypatch):
    set_fake_result(monkeypatch, (28,))

    result = query_data.question_9()

    assert result == 28


@pytest.mark.db
def test_question_10(monkeypatch, capsys):
    set_fake_result(monkeypatch, (37.10,))

    query_data.question_10()

    output = capsys.readouterr().out

    assert "Fall 2026 acceptance percentage: 37.10%" in output


@pytest.mark.db
def test_question_11(monkeypatch, capsys):
    set_fake_result(monkeypatch, (3.93,))

    query_data.question_11()

    output = capsys.readouterr().out

    assert (
        "Average GPA of international Fall 2026 applicants: 3.93"
        in output
    )


@pytest.mark.db
def test_main(monkeypatch, capsys):
    monkeypatch.setattr(
        query_data,
        "question_1",
        lambda: None,
    )

    monkeypatch.setattr(
        query_data,
        "question_2",
        lambda: None,
    )

    monkeypatch.setattr(
        query_data,
        "question_3",
        lambda: None,
    )

    monkeypatch.setattr(
        query_data,
        "question_4",
        lambda: None,
    )

    monkeypatch.setattr(
        query_data,
        "question_5",
        lambda: None,
    )

    monkeypatch.setattr(
        query_data,
        "question_6",
        lambda: None,
    )

    monkeypatch.setattr(
        query_data,
        "question_7",
        lambda: None,
    )

    monkeypatch.setattr(
        query_data,
        "question_8",
        lambda: 28,
    )

    monkeypatch.setattr(
        query_data,
        "question_9",
        lambda: 30,
    )

    monkeypatch.setattr(
        query_data,
        "question_10",
        lambda: None,
    )

    monkeypatch.setattr(
        query_data,
        "question_11",
        lambda: None,
    )

    query_data.main()

    output = capsys.readouterr().out

    assert "Original-field count: 28" in output
    assert "LLM-field count: 30" in output
    assert "Difference: 2" in output