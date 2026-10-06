import re

import pytest

from src.app import create_app


@pytest.mark.analysis
def test_analysis_labels_and_percentage_formatting():
    fake_results = {
        "q1": 10,
        "q2": 39.28,
        "gpa": 3.85,
        "gre": 262.93,
        "gre_v": 161.53,
        "gre_aw": 8.34,
        "q4": 3.79,
        "q5": 47.92,
        "q6": 3.88,
        "q7": 8,
        "q8": 28,
        "q9": 28,
        "difference": 0,
        "q10": 37.10,
        "q11": 3.93,
    }

    app = create_app(
        {"TESTING": True},
        query_func=lambda: fake_results,
    )

    client = app.test_client()

    response = client.get("/analysis")
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Answer:" in page

    percentages = re.findall(r"\d+\.\d+%", page)

    assert percentages
    assert all(
        re.fullmatch(r"\d+\.\d{2}%", percentage)
        for percentage in percentages
    )