import subprocess
import sys
from types import SimpleNamespace

import pytest
from bs4 import BeautifulSoup

from src import scrape


@pytest.mark.web
def test_get_current_url(monkeypatch):
    monkeypatch.setattr(
        scrape.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(
            stdout="https://www.thegradcafe.com/survey\n"
        ),
    )

    scraper = scrape.GradCafeScraper()

    assert (
        scraper.get_current_url()
        == "https://www.thegradcafe.com/survey"
    )


@pytest.mark.web
def test_capture_current_page(monkeypatch):
    scraper = scrape.GradCafeScraper()

    monkeypatch.setattr(
        scraper,
        "get_current_url",
        lambda: "https://www.thegradcafe.com/survey",
    )

    monkeypatch.setattr(
        scrape.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(
            stdout="<html><table></table></html>"
        ),
    )

    url, html = scraper.capture_current_page()

    assert url == "https://www.thegradcafe.com/survey"
    assert "<table>" in html


@pytest.mark.web
def test_navigate_to(monkeypatch):
    scraper = scrape.GradCafeScraper()

    target_url = (
        "https://www.thegradcafe.com/survey?page=2"
    )

    monkeypatch.setattr(
        scrape.subprocess,
        "run",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        scraper,
        "get_current_url",
        lambda: target_url,
    )

    monkeypatch.setattr(
        scrape.time,
        "sleep",
        lambda seconds: None,
    )

    scraper.navigate_to(target_url)


@pytest.mark.web
def test_navigate_to_handles_browser_error(monkeypatch):
    scraper = scrape.GradCafeScraper()

    target_url = (
        "https://www.thegradcafe.com/survey?page=2"
    )

    monkeypatch.setattr(
        scrape.subprocess,
        "run",
        lambda *args, **kwargs: None,
    )

    calls = {"count": 0}

    def fake_current_url():
        calls["count"] += 1

        if calls["count"] == 1:
            raise subprocess.CalledProcessError(
                1,
                "osascript",
            )

        return target_url

    monkeypatch.setattr(
        scraper,
        "get_current_url",
        fake_current_url,
    )

    monkeypatch.setattr(
        scrape.time,
        "sleep",
        lambda seconds: None,
    )

    scraper.navigate_to(target_url)

    assert calls["count"] == 2


@pytest.mark.web
def test_navigate_to_timeout(monkeypatch):
    scraper = scrape.GradCafeScraper()

    target_url = (
        "https://www.thegradcafe.com/survey?page=2"
    )

    monkeypatch.setattr(
        scrape.subprocess,
        "run",
        lambda *args, **kwargs: None,
    )

    times = iter([0, 61])

    monkeypatch.setattr(
        scrape.time,
        "time",
        lambda: next(times),
    )

    with pytest.raises(RuntimeError):
        scraper.navigate_to(target_url)


@pytest.mark.web
def test_wait_for_results(monkeypatch):
    scraper = scrape.GradCafeScraper()

    html = """
    <html>
        <table>
            <tr>
                <td>
                    <a href="/result/123">
                        Result
                    </a>
                </td>
            </tr>
        </table>
    </html>
    """

    monkeypatch.setattr(
        scraper,
        "capture_current_page",
        lambda: (
            "https://www.thegradcafe.com/survey",
            html,
        ),
    )

    url, result_html = scraper.wait_for_results()

    assert url == "https://www.thegradcafe.com/survey"
    assert result_html == html


@pytest.mark.web
def test_wait_for_results_timeout(monkeypatch):
    scraper = scrape.GradCafeScraper()

    def fake_capture():
        raise ValueError("Test error")

    monkeypatch.setattr(
        scraper,
        "capture_current_page",
        fake_capture,
    )

    monkeypatch.setattr(
        scrape.time,
        "sleep",
        lambda seconds: None,
    )

    times = iter([0, 1, 61])

    monkeypatch.setattr(
        scrape.time,
        "time",
        lambda: next(times),
    )

    with pytest.raises(RuntimeError):
        scraper.wait_for_results()


@pytest.mark.web
def test_get_next_url():
    scraper = scrape.GradCafeScraper()

    html = """
    <html>
        <a href="/survey?page=2">Next</a>
    </html>
    """

    result = scraper.get_next_url(html)

    assert result == (
        "https://www.thegradcafe.com/survey?page=2"
    )


@pytest.mark.web
def test_get_next_url_none():
    scraper = scrape.GradCafeScraper()

    html = """
    <html>
        <a href="/survey?page=1">Previous</a>
    </html>
    """

    assert scraper.get_next_url(html) is None


@pytest.mark.web
def test_scrape_data_without_table():
    scraper = scrape.GradCafeScraper()

    with pytest.raises(ValueError):
        scraper.scrape_data("<html></html>")


@pytest.mark.web
def test_scrape_data():
    scraper = scrape.GradCafeScraper()

    html = """
    <html>
        <table>
            <tr>
                <td>Johns Hopkins University</td>
                <td>
                    <span>Computer Science</span>
                    <span>Masters</span>
                </td>
                <td>Sep 20, 2026</td>
                <td>
                    <a href="/result/1001">
                        Accepted on Sep 20
                    </a>
                </td>
            </tr>
            <tr>
                <td colspan="4">
                    Fall 2026 International GPA 3.90
                    GRE, Quantitative: 165,
                    Verbal: 160,
                    Analytical Writing: 4.5
                    Great program
                </td>
            </tr>

            <tr>
                <td>Stanford University</td>
                <td>Data Science</td>
                <td>Sep 21, 2026</td>
                <td>
                    <a href="/result/1002">
                        Rejected on Sep 21
                    </a>
                </td>
            </tr>
            <tr>
                <td colspan="4">
                    Fall 2026 American GPA 3.80
                </td>
            </tr>
        </table>
    </html>
    """

    applicants = scraper.scrape_data(html)

    assert len(applicants) == 2

    first = applicants[0]

    assert first["program_name"] == "Computer Science"
    assert first["university"] == "Johns Hopkins University"
    assert first["degree_type"] == "Masters"
    assert first["status"] == "Accepted"
    assert first["acceptance_date"] == "Sep 20"
    assert first["rejection_date"] is None
    assert first["program_start"] == "Fall 2026"
    assert first["applicant_type"] == "International"
    assert first["gpa"] == 3.90
    assert first["gre_score"] == 165
    assert first["gre_verbal"] == 160
    assert first["gre_aw"] == 4.5

    second = applicants[1]

    assert second["program_name"] == "Data Science"
    assert second["degree_type"] is None
    assert second["status"] == "Rejected"
    assert second["acceptance_date"] is None
    assert second["rejection_date"] == "Sep 21"


@pytest.mark.web
def test_parse_entry_too_few_cells():
    scraper = scrape.GradCafeScraper()

    soup = BeautifulSoup(
        "<table><tr><td>Only one</td></tr></table>",
        "html.parser",
    )

    rows = soup.find_all("tr")

    assert scraper._parse_entry(rows) is None


@pytest.mark.web
def test_parse_entry_without_result_link():
    scraper = scrape.GradCafeScraper()

    html = """
    <table>
        <tr>
            <td>Test University</td>
            <td>History</td>
            <td>Sep 22, 2026</td>
            <td>Pending</td>
        </tr>
    </table>
    """

    soup = BeautifulSoup(html, "html.parser")
    rows = soup.find_all("tr")

    result = scraper._parse_entry(rows)

    assert result["program_name"] == "History"
    assert result["degree_type"] is None
    assert result["applicant_url"] is None
    assert result["status"] == "Pending"
    assert result["decision_date"] is None
    assert result["program_start"] is None
    assert result["applicant_type"] is None
    assert result["gpa"] is None


@pytest.mark.web
def test_extract_comments():
    scraper = scrape.GradCafeScraper()

    detail = (
        "Fall 2026 International GPA 3.90 "
        "GRE, Quantitative: 165, "
        "Verbal: 160, "
        "Analytical Writing: 4.5 "
        "Great program"
    )

    result = scraper._extract_comments(
        detail,
        "Accepted on Sep 20",
    )

    assert result == "Great program"


@pytest.mark.web
def test_extract_comments_empty():
    scraper = scrape.GradCafeScraper()

    assert scraper._extract_comments("", "Accepted") is None


@pytest.mark.web
@pytest.mark.parametrize(
    "decision, expected",
    [
        ("Accepted on Sep 20", "Accepted"),
        ("Rejected on Sep 20", "Rejected"),
        ("Wait Listed", "Wait Listed"),
        ("Waitlisted", "Wait Listed"),
        ("Interview", "Interview"),
        ("Deferred on Sep 20", "Deferred"),
        ("", None),
    ],
)
def test_normalize_status(decision, expected):
    scraper = scrape.GradCafeScraper()

    assert scraper._normalize_status(decision) == expected


@pytest.mark.web
def test_extract_number():
    scraper = scrape.GradCafeScraper()

    patterns = [
        r"GRE,\s*Quantitative:\s*(\d+)",
        r"\bGRE\s+(\d{2,3})\b",
    ]

    assert (
        scraper._extract_number(
            "GRE, Quantitative: 165",
            patterns,
        )
        == 165
    )

    assert (
        scraper._extract_number(
            "No GRE score",
            patterns,
        )
        is None
    )


@pytest.mark.web
def test_extract_float():
    scraper = scrape.GradCafeScraper()

    patterns = [
        r"GRE\s*AW\s*(\d+(?:\.\d+)?)",
    ]

    assert (
        scraper._extract_float(
            "GRE AW 4.5",
            patterns,
        )
        == 4.5
    )

    assert (
        scraper._extract_float(
            "No writing score",
            patterns,
        )
        is None
    )


@pytest.mark.web
def test_validate_results_url():
    scraper = scrape.GradCafeScraper()

    scraper._validate_results_url(
        "https://www.thegradcafe.com/survey"
    )

    scraper._validate_results_url(
        "https://thegradcafe.com/survey?page=2"
    )


@pytest.mark.web
def test_validate_results_url_bad_domain():
    scraper = scrape.GradCafeScraper()

    with pytest.raises(ValueError):
        scraper._validate_results_url(
            "https://example.com/survey"
        )


@pytest.mark.web
def test_validate_results_url_bad_path():
    scraper = scrape.GradCafeScraper()

    with pytest.raises(ValueError):
        scraper._validate_results_url(
            "https://www.thegradcafe.com/result/123"
        )


@pytest.mark.web
def test_save_and_load_data(tmp_path):
    test_file = tmp_path / "applicants.json"

    data = [
        {
            "applicant_url": (
                "https://www.thegradcafe.com/result/1"
            )
        }
    ]

    scrape.save_data(
        data,
        filename=test_file,
    )

    result = scrape.load_data(
        filename=test_file,
    )

    assert result == data


@pytest.mark.web
def test_load_data_missing_file(tmp_path):
    test_file = tmp_path / "missing.json"

    assert scrape.load_data(test_file) == []


@pytest.mark.web
def test_merge_data():
    existing = [
        {
            "applicant_url": (
                "https://www.thegradcafe.com/result/1"
            )
        }
    ]

    new_records = [
        {
            "applicant_url": (
                "https://www.thegradcafe.com/result/1"
            )
        },
        {
            "applicant_url": (
                "https://www.thegradcafe.com/result/2"
            )
        },
        {
            "applicant_url": None,
        },
    ]

    added = scrape.merge_data(
        existing,
        new_records,
    )

    assert added == 1
    assert len(existing) == 2


@pytest.mark.web
def test_save_raw_html(tmp_path, monkeypatch):
    cache_dir = tmp_path / "raw_html"

    monkeypatch.setattr(
        scrape,
        "CACHE_DIR",
        cache_dir,
    )

    scrape.save_raw_html(
        "<html>Test</html>",
        3,
    )

    saved_file = (
        cache_dir / "page_00003.html"
    )

    assert saved_file.exists()

    assert (
        saved_file.read_text(encoding="utf-8")
        == "<html>Test</html>"
    )


@pytest.mark.web
def test_save_and_load_state(tmp_path, monkeypatch):
    state_file = tmp_path / "scrape_state.json"

    monkeypatch.setattr(
        scrape,
        "STATE_FILE",
        state_file,
    )

    assert scrape.load_state() is None

    scrape.save_state(
        "https://www.thegradcafe.com/survey?page=2",
        10,
        1,
    )

    result = scrape.load_state()

    assert result["next_url"] == (
        "https://www.thegradcafe.com/survey?page=2"
    )

    assert result["total_records"] == 10
    assert result["page_number"] == 1


@pytest.mark.web
def test_main_pages_and_target_error(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "scrape.py",
            "--pages",
            "1",
            "--target",
            "10",
        ],
    )

    with pytest.raises(SystemExit):
        scrape.main()


@pytest.mark.web
def test_main_one_page(monkeypatch, capsys):
    html = """
    <table>
        <tr>
            <td>
                <a href="/result/1">Result</a>
            </td>
        </tr>
    </table>
    """

    class FakeScraper:
        def wait_for_results(self):
            return (
                "https://www.thegradcafe.com/survey",
                html,
            )

        def scrape_data(self, page_html):
            return [
                {
                    "applicant_url": (
                        "https://www.thegradcafe.com/result/1"
                    )
                }
            ]

        def get_next_url(self, page_html):
            return (
                "https://www.thegradcafe.com/survey?page=2"
            )

        def navigate_to(self, url):
            return None

    monkeypatch.setattr(
        sys,
        "argv",
        ["scrape.py"],
    )

    monkeypatch.setattr(
        scrape,
        "GradCafeScraper",
        FakeScraper,
    )

    monkeypatch.setattr(
        scrape,
        "load_data",
        lambda: [],
    )

    monkeypatch.setattr(
        scrape,
        "load_state",
        lambda: None,
    )

    monkeypatch.setattr(
        scrape,
        "save_raw_html",
        lambda html, page_number: None,
    )

    monkeypatch.setattr(
        scrape,
        "save_data",
        lambda data: None,
    )

    monkeypatch.setattr(
        scrape,
        "save_state",
        lambda *args: None,
    )

    scrape.main()

    output = capsys.readouterr().out

    assert "Page 1:" in output
    assert "Finished." in output


@pytest.mark.web
def test_main_resume_with_saved_state(
    monkeypatch,
    capsys,
):
    navigated = []

    class FakeScraper:
        def navigate_to(self, url):
            navigated.append(url)

        def wait_for_results(self):
            return (
                "https://www.thegradcafe.com/survey?page=2",
                "<html></html>",
            )

        def scrape_data(self, html):
            return []

        def get_next_url(self, html):
            return None

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "scrape.py",
            "--resume",
            "--pages",
            "1",
        ],
    )

    monkeypatch.setattr(
        scrape,
        "GradCafeScraper",
        FakeScraper,
    )

    monkeypatch.setattr(
        scrape,
        "load_data",
        lambda: [],
    )

    monkeypatch.setattr(
        scrape,
        "load_state",
        lambda: {
            "next_url": (
                "https://www.thegradcafe.com/survey?page=2"
            ),
            "total_records": 0,
            "page_number": 1,
        },
    )

    monkeypatch.setattr(
        scrape,
        "save_raw_html",
        lambda *args: None,
    )

    monkeypatch.setattr(
        scrape,
        "save_data",
        lambda data: None,
    )

    monkeypatch.setattr(
        scrape,
        "save_state",
        lambda *args: None,
    )

    scrape.main()

    output = capsys.readouterr().out

    assert "Resuming from" in output

    assert navigated[0] == (
        "https://www.thegradcafe.com/survey?page=2"
    )

    assert "Page 2:" in output


@pytest.mark.web
def test_main_resume_without_saved_state(
    monkeypatch,
    capsys,
):
    class FakeScraper:
        def wait_for_results(self):
            return (
                "https://www.thegradcafe.com/survey",
                "<html></html>",
            )

        def scrape_data(self, html):
            return []

        def get_next_url(self, html):
            return None

        def navigate_to(self, url):
            return None

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "scrape.py",
            "--resume",
            "--pages",
            "1",
        ],
    )

    monkeypatch.setattr(
        scrape,
        "GradCafeScraper",
        FakeScraper,
    )

    monkeypatch.setattr(
        scrape,
        "load_data",
        lambda: [],
    )

    monkeypatch.setattr(
        scrape,
        "load_state",
        lambda: None,
    )

    monkeypatch.setattr(
        scrape,
        "save_raw_html",
        lambda *args: None,
    )

    monkeypatch.setattr(
        scrape,
        "save_data",
        lambda data: None,
    )

    monkeypatch.setattr(
        scrape,
        "save_state",
        lambda *args: None,
    )

    scrape.main()

    output = capsys.readouterr().out

    assert (
        "No saved resume point was found."
        in output
    )


@pytest.mark.web
def test_main_target_reached(monkeypatch, capsys):
    class FakeScraper:
        def wait_for_results(self):
            return (
                "https://www.thegradcafe.com/survey",
                "<html></html>",
            )

        def scrape_data(self, html):
            return [
                {
                    "applicant_url": (
                        "https://www.thegradcafe.com/result/1"
                    )
                }
            ]

        def get_next_url(self, html):
            return None

        def navigate_to(self, url):
            return None

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "scrape.py",
            "--target",
            "1",
        ],
    )

    monkeypatch.setattr(
        scrape,
        "GradCafeScraper",
        FakeScraper,
    )

    monkeypatch.setattr(
        scrape,
        "load_data",
        lambda: [],
    )

    monkeypatch.setattr(
        scrape,
        "load_state",
        lambda: None,
    )

    monkeypatch.setattr(
        scrape,
        "save_raw_html",
        lambda *args: None,
    )

    monkeypatch.setattr(
        scrape,
        "save_data",
        lambda data: None,
    )

    monkeypatch.setattr(
        scrape,
        "save_state",
        lambda *args: None,
    )

    scrape.main()

    output = capsys.readouterr().out

    assert "Target reached: 1 records." in output


@pytest.mark.web
def test_main_no_next_page(monkeypatch, capsys):
    class FakeScraper:
        def wait_for_results(self):
            return (
                "https://www.thegradcafe.com/survey",
                "<html></html>",
            )

        def scrape_data(self, html):
            return []

        def get_next_url(self, html):
            return None

        def navigate_to(self, url):
            return None

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "scrape.py",
            "--pages",
            "2",
        ],
    )

    monkeypatch.setattr(
        scrape,
        "GradCafeScraper",
        FakeScraper,
    )

    monkeypatch.setattr(
        scrape,
        "load_data",
        lambda: [],
    )

    monkeypatch.setattr(
        scrape,
        "load_state",
        lambda: None,
    )

    monkeypatch.setattr(
        scrape,
        "save_raw_html",
        lambda *args: None,
    )

    monkeypatch.setattr(
        scrape,
        "save_data",
        lambda data: None,
    )

    monkeypatch.setattr(
        scrape,
        "save_state",
        lambda *args: None,
    )

    scrape.main()

    output = capsys.readouterr().out

    assert "No Next page link was found." in output


@pytest.mark.web
def test_main_moves_to_next_page(monkeypatch):
    navigated = []
    calls = {"page": 0}

    class FakeScraper:
        def wait_for_results(self):
            calls["page"] += 1

            return (
                "https://www.thegradcafe.com/survey",
                "<html></html>",
            )

        def scrape_data(self, html):
            return []

        def get_next_url(self, html):
            if calls["page"] == 1:
                return (
                    "https://www.thegradcafe.com/survey?page=2"
                )

            return None

        def navigate_to(self, url):
            navigated.append(url)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "scrape.py",
            "--pages",
            "2",
            "--delay",
            "0",
        ],
    )

    monkeypatch.setattr(
        scrape,
        "GradCafeScraper",
        FakeScraper,
    )

    monkeypatch.setattr(
        scrape,
        "load_data",
        lambda: [],
    )

    monkeypatch.setattr(
        scrape,
        "load_state",
        lambda: None,
    )

    monkeypatch.setattr(
        scrape,
        "save_raw_html",
        lambda *args: None,
    )

    monkeypatch.setattr(
        scrape,
        "save_data",
        lambda data: None,
    )

    monkeypatch.setattr(
        scrape,
        "save_state",
        lambda *args: None,
    )

    monkeypatch.setattr(
        scrape.time,
        "sleep",
        lambda seconds: None,
    )

    scrape.main()

    assert navigated == [
        "https://www.thegradcafe.com/survey?page=2"
    ]