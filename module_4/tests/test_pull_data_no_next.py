import pytest

from src import pull_data


@pytest.mark.db
def test_collect_new_records_no_next_page(monkeypatch):
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
                }
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

    records = pull_data.collect_new_records()

    assert len(records) == 1
    assert (
        records[0]["applicant_url"]
        == "https://www.thegradcafe.com/result/101"
    )