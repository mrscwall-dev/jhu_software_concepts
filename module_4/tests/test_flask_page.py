import pytest
from src.app import create_app


@pytest.mark.web
def test_create_app():
    app = create_app()

    assert app is not None


@pytest.mark.web
def test_routes_exist():
    app = create_app()

    routes = [rule.rule for rule in app.url_map.iter_rules()]

    assert "/" in routes
    assert "/analysis" in routes
    assert "/pull-data" in routes
    assert "/update-analysis" in routes


@pytest.mark.web
def test_analysis_page(monkeypatch):
    fake_results = {
        "q1": 10,
        "q2": 39.28,
        "gpa": 3.85,
        "gre": 162.00,
        "gre_v": 160.00,
        "gre_aw": 4.50,
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

    monkeypatch.setattr(
        "src.app.get_analysis_results",
        lambda: fake_results,
    )

    monkeypatch.setattr(
        "src.app.pull_is_running",
        lambda: False,
    )

    app = create_app({"TESTING": True})
    client = app.test_client()

    response = client.get("/analysis")
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Analysis" in page
    assert "Pull Data" in page
    assert "Update Analysis" in page
    assert "Answer:" in page
    assert 'data-testid="pull-data-btn"' in page
    assert 'data-testid="update-analysis-btn"' in page