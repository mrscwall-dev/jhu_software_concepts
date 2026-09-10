from __future__ import annotations

import argparse
import json
import re
import subprocess
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup


BASE_URL = "https://www.thegradcafe.com"
OUTPUT_FILE = Path("applicant_data.json")

# Temporary files stay outside the Git repository.
CACHE_DIR = Path.home() / ".cache" / "jhu_module2" / "raw_html"
STATE_FILE = Path.home() / ".cache" / "jhu_module2" / "scrape_state.json"


class GradCafeScraper:
    """Capture and parse publicly available GradCafe admissions results."""

    def get_current_url(self) -> str:
        """Return the URL of the active Chrome tab."""

        script = """
        tell application "Google Chrome"
            get URL of active tab of front window
        end tell
        """

        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            check=True,
        )

        return result.stdout.strip()

    def capture_current_page(self) -> tuple[str, str]:
        """Capture HTML from the active GradCafe results page."""

        current_url = self.get_current_url()
        self._validate_results_url(current_url)

        script = """
        tell application "Google Chrome"
            execute active tab of front window javascript "document.documentElement.outerHTML"
        end tell
        """

        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            check=True,
        )

        return current_url, result.stdout

    def navigate_to(self, url: str) -> None:
        """Navigate Chrome to a GradCafe results page and wait for loading."""

        self._validate_results_url(url)

        safe_url = url.replace("\\", "\\\\").replace('"', '\\"')

        navigation_script = f"""
        tell application "Google Chrome"
            set URL of active tab of front window to "{safe_url}"
        end tell
        """

        subprocess.run(
            ["osascript", "-e", navigation_script],
            capture_output=True,
            text=True,
            check=True,
        )

        target = urlparse(url)
        deadline = time.time() + 60

        while time.time() < deadline:
            current = urlparse(self.get_current_url())

            correct_page = (
                current.netloc == target.netloc
                and current.path == target.path
                and current.query == target.query
            )

            if correct_page:
                ready_script = """
                tell application "Google Chrome"
                    execute active tab of front window javascript "document.readyState"
                end tell
                """

                result = subprocess.run(
                    ["osascript", "-e", ready_script],
                    capture_output=True,
                    text=True,
                    check=True,
                )

                if result.stdout.strip() == "complete":
                    time.sleep(1)
                    return

            time.sleep(0.5)

        raise RuntimeError(
            "Chrome did not finish loading the next GradCafe page."
        )

    def wait_for_results(
        self,
        timeout: int = 60,
    ) -> tuple[str, str]:
        """Wait until a GradCafe results table is available."""

        deadline = time.time() + timeout

        while time.time() < deadline:
            try:
                current_url, html = self.capture_current_page()

                soup = BeautifulSoup(
                    html,
                    "html.parser",
                )

                table = soup.find("table")

                result_links = soup.find_all(
                    "a",
                    href=lambda href: (
                        href
                        and href.startswith("/result/")
                    ),
                )

                if table is not None and result_links:
                    return current_url, html

            except (
                ValueError,
                subprocess.CalledProcessError,
            ):
                pass

            time.sleep(1)

        raise RuntimeError(
            "The GradCafe results table did not appear. "
            "If Cloudflare is requesting verification, complete "
            "the verification manually in Chrome and run again."
        )

    def get_next_url(self, html: str) -> str | None:
        """Find the next GradCafe results-page URL."""

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        for link in soup.find_all("a", href=True):
            text = link.get_text(
                " ",
                strip=True,
            ).lower()

            if text == "next":
                next_url = urljoin(
                    BASE_URL,
                    link["href"],
                )

                self._validate_results_url(next_url)

                return next_url

        return None

    def scrape_data(self, html: str) -> list[dict]:
        """Parse applicant records from one GradCafe results page."""

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        table = soup.find("table")

        if table is None:
            raise ValueError(
                "No GradCafe results table was found."
            )

        rows = table.find_all("tr")

        grouped_records = []
        current_group = []

        for row in rows:
            result_link = row.find(
                "a",
                href=lambda href: (
                    href
                    and href.startswith("/result/")
                ),
            )

            if result_link:
                if current_group:
                    grouped_records.append(
                        current_group
                    )

                current_group = [row]

            elif current_group:
                current_group.append(row)

        if current_group:
            grouped_records.append(
                current_group
            )

        applicants = []

        for group in grouped_records:
            applicant = self._parse_entry(group)

            if applicant:
                applicants.append(applicant)

        return applicants

    def _parse_entry(self, rows) -> dict | None:
        """Convert one applicant's rows into a structured record."""

        summary_row = rows[0]
        cells = summary_row.find_all("td")

        if len(cells) < 4:
            return None

        university = cells[0].get_text(
            " ",
            strip=True,
        )

        program_cell = cells[1]
        spans = program_cell.find_all("span")

        if spans:
            program_name = spans[0].get_text(
                " ",
                strip=True,
            )

            degree_type = (
                spans[1].get_text(
                    " ",
                    strip=True,
                )
                if len(spans) > 1
                else None
            )

        else:
            program_name = program_cell.get_text(
                " ",
                strip=True,
            )

            degree_type = None

        raw_program_text = program_cell.get_text(
            " ",
            strip=True,
        )

        date_added = cells[2].get_text(
            " ",
            strip=True,
        )

        decision_raw = cells[3].get_text(
            " ",
            strip=True,
        )

        result_link = summary_row.find(
            "a",
            href=lambda href: (
                href
                and href.startswith("/result/")
            ),
        )

        applicant_url = (
            urljoin(
                BASE_URL,
                result_link["href"],
            )
            if result_link
            else None
        )

        detail_text = " ".join(
            row.get_text(
                " ",
                strip=True,
            )
            for row in rows[1:]
        )

        raw_listing_text = " ".join(
            row.get_text(
                " ",
                strip=True,
            )
            for row in rows
        )

        status = self._normalize_status(
            decision_raw
        )

        decision_date_match = re.search(
            r"\bon\s+([A-Z][a-z]{2}\s+\d{1,2})",
            decision_raw,
        )

        decision_date = (
            decision_date_match.group(1)
            if decision_date_match
            else None
        )

        program_start_match = re.search(
            r"\b(Fall|Spring|Summer|Winter)\s+(\d{4})\b",
            detail_text,
            re.IGNORECASE,
        )

        program_start = (
            f"{program_start_match.group(1).title()} "
            f"{program_start_match.group(2)}"
            if program_start_match
            else None
        )

        applicant_type_match = re.search(
            r"\b(International|American|Other)\b",
            detail_text,
            re.IGNORECASE,
        )

        applicant_type = (
            applicant_type_match.group(1).title()
            if applicant_type_match
            else None
        )

        gpa_match = re.search(
            r"\bGPA\s+(\d+(?:\.\d+)?)",
            detail_text,
            re.IGNORECASE,
        )

        gpa = (
            float(gpa_match.group(1))
            if gpa_match
            else None
        )

        gre_score = self._extract_number(
            detail_text,
            [
                r"GRE,\s*Quantitative:\s*(\d+)",
                r"\bGRE\s+(\d{2,3})\b",
            ],
        )

        gre_verbal = self._extract_number(
            detail_text,
            [
                r"Verbal:\s*(\d+)",
                r"GRE\s*V\s*(\d+)",
            ],
        )

        gre_aw = self._extract_float(
            detail_text,
            [
                r"Analytical Writing:\s*(\d+(?:\.\d+)?)",
                r"GRE\s*AW\s*(\d+(?:\.\d+)?)",
            ],
        )

        acceptance_date = (
            decision_date
            if status == "Accepted"
            else None
        )

        rejection_date = (
            decision_date
            if status == "Rejected"
            else None
        )

        comments = self._extract_comments(
            detail_text,
            decision_raw,
        )

        return {
            "raw_listing_text": raw_listing_text,
            "raw_program_text": raw_program_text,
            "program_name": program_name,
            "university": university,
            "comments": comments,
            "date_added": date_added,
            "applicant_url": applicant_url,
            "status": status,
            "decision_date": decision_date,
            "acceptance_date": acceptance_date,
            "rejection_date": rejection_date,
            "program_start": program_start,
            "applicant_type": applicant_type,
            "gre_score": gre_score,
            "gre_verbal": gre_verbal,
            "degree_type": degree_type,
            "gpa": gpa,
            "gre_aw": gre_aw,
        }

    def _extract_comments(
        self,
        detail_text: str,
        decision_raw: str,
    ) -> str | None:
        """Remove structured fields and return free-text comments."""

        text = detail_text.strip()

        patterns = [
            re.escape(decision_raw),
            r"(?:Fall|Spring|Summer|Winter)\s+\d{4}",
            r"(?:International|American|Other)",
            r"GPA\s+\d+(?:\.\d+)?",
            (
                r"GRE,\s*Quantitative:\s*\d+,\s*"
                r"Verbal:\s*\d+,\s*"
                r"Analytical Writing:\s*\d+(?:\.\d+)?"
            ),
            r"GRE\s+\d{2,3}",
            r"GRE\s*V\s+\d{2,3}",
            r"GRE\s*AW\s+\d+(?:\.\d+)?",
        ]

        changed = True

        while changed and text:
            changed = False

            for pattern in patterns:
                cleaned = re.sub(
                    rf"^\s*(?:{pattern})\s*",
                    "",
                    text,
                    count=1,
                    flags=re.IGNORECASE,
                )

                if cleaned != text:
                    text = cleaned
                    changed = True

        return text.strip() or None

    def _normalize_status(
        self,
        decision: str,
    ) -> str | None:
        """Normalize applicant decision text."""

        decision_lower = decision.lower()

        if "accepted" in decision_lower:
            return "Accepted"

        if "rejected" in decision_lower:
            return "Rejected"

        if (
            "wait listed" in decision_lower
            or "waitlisted" in decision_lower
        ):
            return "Wait Listed"

        if "interview" in decision_lower:
            return "Interview"

        return (
            decision.split(" on ")[0].strip()
            if decision
            else None
        )

    def _extract_number(
        self,
        text: str,
        patterns: list[str],
    ) -> int | None:
        """Extract an integer from text."""

        for pattern in patterns:
            match = re.search(
                pattern,
                text,
                re.IGNORECASE,
            )

            if match:
                return int(match.group(1))

        return None

    def _extract_float(
        self,
        text: str,
        patterns: list[str],
    ) -> float | None:
        """Extract a decimal number from text."""

        for pattern in patterns:
            match = re.search(
                pattern,
                text,
                re.IGNORECASE,
            )

            if match:
                return float(match.group(1))

        return None

    def _validate_results_url(
        self,
        url: str,
    ) -> None:
        """Allow only the public GradCafe survey page."""

        parsed = urlparse(url)

        if parsed.netloc not in {
            "www.thegradcafe.com",
            "thegradcafe.com",
        }:
            raise ValueError(
                "The URL is not on the GradCafe website."
            )

        if parsed.path != "/survey":
            raise ValueError(
                "Only the public GradCafe survey results page is allowed."
            )


def save_data(
    data: list[dict],
    filename: Path = OUTPUT_FILE,
) -> None:
    """Save applicant records as JSON."""

    with filename.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False,
        )


def load_data(
    filename: Path = OUTPUT_FILE,
) -> list[dict]:
    """Load previously saved applicant records."""

    if not filename.exists():
        return []

    with filename.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def merge_data(
    existing: list[dict],
    new_records: list[dict],
) -> int:
    """Add new applicants without duplicating URLs."""

    existing_urls = {
        record.get("applicant_url")
        for record in existing
        if record.get("applicant_url")
    }

    added = 0

    for record in new_records:
        applicant_url = record.get(
            "applicant_url"
        )

        if (
            applicant_url
            and applicant_url not in existing_urls
        ):
            existing.append(record)
            existing_urls.add(applicant_url)
            added += 1

    return added


def save_raw_html(
    html: str,
    page_number: int,
) -> None:
    """Save temporary raw HTML outside the Git repository."""

    CACHE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    filename = (
        CACHE_DIR
        / f"page_{page_number:05d}.html"
    )

    filename.write_text(
        html,
        encoding="utf-8",
    )


def save_state(
    next_url: str | None,
    total_records: int,
    page_number: int,
) -> None:
    """Save restart information outside the repository."""

    STATE_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    state = {
        "next_url": next_url,
        "total_records": total_records,
        "page_number": page_number,
    }

    STATE_FILE.write_text(
        json.dumps(
            state,
            indent=2,
        ),
        encoding="utf-8",
    )


def load_state() -> dict | None:
    """Load restart information."""

    if not STATE_FILE.exists():
        return None

    return json.loads(
        STATE_FILE.read_text(
            encoding="utf-8"
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Capture and parse GradCafe applicant results."
        )
    )

    parser.add_argument(
        "--pages",
        type=int,
        help="Number of results pages to process.",
    )

    parser.add_argument(
        "--target",
        type=int,
        help="Continue until this many unique records exist.",
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=4.0,
        help="Seconds to wait between pages.",
    )

    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from the previously saved next-page URL.",
    )

    args = parser.parse_args()

    if (
        args.pages is not None
        and args.target is not None
    ):
        parser.error(
            "Use either --pages or --target, not both."
        )

    pages_to_process = (
        args.pages
        if args.pages is not None
        else 1
    )

    scraper = GradCafeScraper()
    all_data = load_data()

    saved_state = load_state()

    if args.resume:
        if (
            saved_state
            and saved_state.get("next_url")
        ):
            print(
                "Resuming from the previously saved GradCafe page..."
            )

            scraper.navigate_to(
                saved_state["next_url"]
            )

        else:
            print(
                "No saved resume point was found. "
                "Using the current Chrome page."
            )

    page_number = 1

    if saved_state:
        page_number = (
            int(
                saved_state.get(
                    "page_number",
                    0,
                )
            )
            + 1
        )

    pages_processed = 0

    while True:
        current_url, html = (
            scraper.wait_for_results()
        )

        applicants = scraper.scrape_data(
            html
        )

        save_raw_html(
            html,
            page_number,
        )

        added = merge_data(
            all_data,
            applicants,
        )

        save_data(all_data)

        next_url = scraper.get_next_url(
            html
        )

        save_state(
            next_url,
            len(all_data),
            page_number,
        )

        pages_processed += 1

        print(
            f"Page {page_number}: "
            f"{len(applicants)} found, "
            f"{added} new, "
            f"{len(all_data)} total saved."
        )

        if (
            args.target is not None
            and len(all_data) >= args.target
        ):
            print(
                f"Target reached: "
                f"{len(all_data)} records."
            )
            break

        if (
            args.target is None
            and pages_processed >= pages_to_process
        ):
            break

        if next_url is None:
            print(
                "No Next page link was found."
            )
            break

        print(
            f"Waiting {args.delay} seconds "
            f"before the next page..."
        )

        time.sleep(args.delay)

        scraper.navigate_to(
            next_url
        )

        page_number += 1

    print(
        f"Finished. {len(all_data)} unique "
        f"applicant records are stored in "
        f"{OUTPUT_FILE}."
    )


if __name__ == "__main__":
    main()