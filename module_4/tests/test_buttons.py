import pytest

import src.app as app_module
from src.app import create_app


@pytest.fixture(autouse=True)
def reset_pull_process():
    app_module.pull_process = None

    yield

    app_module.pull_process = None


@pytest.mark.buttons
def test_pull_data():
    fake_rows = [
        {"p_id": 1},
        {"p_id": 2},
    ]

    loaded_rows = []

    def fake_scraper():
        return fake_rows

    def fake_loader(rows):
        loaded_rows.extend(rows)

    app = create_app(
        {"TESTING": True},
        scraper=fake_scraper,
        loader=fake_loader,
    )

    client = app.test_client()

    response = client.post("/pull-data")

    assert response.status_code in (200, 202)
    assert response.get_json() == {"ok": True}
    assert loaded_rows == fake_rows


@pytest.mark.buttons
def test_update_analysis():
    def fake_query():
        return {"q1": 10}

    app = create_app(
        {"TESTING": True},
        query_func=fake_query,
    )

    client = app.test_client()

    response = client.post("/update-analysis")

    assert response.status_code == 200
    assert response.get_json() == {"ok": True}


@pytest.mark.buttons
def test_busy_state():
    loader_called = False

    def fake_scraper():
        return [{"p_id": 1}]

    def fake_loader(rows):
        nonlocal loader_called
        loader_called = True

    app = create_app(
        {
            "TESTING": True,
            "PULL_IN_PROGRESS": True,
        },
        scraper=fake_scraper,
        loader=fake_loader,
        query_func=lambda: {},
    )

    client = app.test_client()

    update_response = client.post(
        "/update-analysis"
    )

    pull_response = client.post(
        "/pull-data"
    )

    assert update_response.status_code == 409
    assert update_response.get_json() == {
        "busy": True
    }

    assert pull_response.status_code == 409
    assert pull_response.get_json() == {
        "busy": True
    }

    assert loader_called is False


@pytest.mark.buttons
def test_pull_is_running():
    class RunningProcess:
        def poll(self):
            return None

    app_module.pull_process = RunningProcess()

    assert app_module.pull_is_running() is True


@pytest.mark.buttons
def test_pull_process_finished():
    class FinishedProcess:
        def poll(self):
            return 0

    app_module.pull_process = FinishedProcess()

    assert app_module.pull_is_running() is False
    assert app_module.pull_process is None


@pytest.mark.buttons
def test_pull_busy_when_process_running():
    class RunningProcess:
        def poll(self):
            return None

    app_module.pull_process = RunningProcess()

    app = create_app(
        {"TESTING": True},
        query_func=lambda: {},
    )

    client = app.test_client()

    response = client.post("/pull-data")

    assert response.status_code == 409
    assert response.get_json() == {
        "busy": True
    }


@pytest.mark.buttons
def test_update_busy_when_process_running():
    class RunningProcess:
        def poll(self):
            return None

    app_module.pull_process = RunningProcess()

    app = create_app(
        {"TESTING": True},
        query_func=lambda: {},
    )

    client = app.test_client()

    response = client.post(
        "/update-analysis"
    )

    assert response.status_code == 409
    assert response.get_json() == {
        "busy": True
    }


@pytest.mark.buttons
def test_pull_starts_process(monkeypatch):
    started = []

    class FakeProcess:
        def poll(self):
            return None

    def fake_popen(command, cwd):
        started.append(
            {
                "command": command,
                "cwd": cwd,
            }
        )

        return FakeProcess()

    monkeypatch.setattr(
        app_module.subprocess,
        "Popen",
        fake_popen,
    )

    app = create_app(
        {"TESTING": True},
        query_func=lambda: {},
    )

    client = app.test_client()

    response = client.post("/pull-data")

    assert response.status_code == 202
    assert response.get_json() == {
        "ok": True
    }

    assert len(started) == 1

    assert started[0]["command"] == [
        app_module.sys.executable,
        "-m",
        "src.pull_data",
    ]

    assert (
        started[0]["cwd"]
        == app_module.MODULE_DIR
    )