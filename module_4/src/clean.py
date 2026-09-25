import json
from pathlib import Path


INPUT_FILE = Path("applicant_data.json")
OUTPUT_FILE = Path("llm_input.json")


def clean_data():
    """Prepare scraped GradCafe data for the professor's LLM standardizer."""

    with INPUT_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    for record in data:
        program_name = record.get("program_name") or ""
        university = record.get("university") or ""

        # The professor's LLM code expects a field named "program"
        # containing the program/university information.
        record["program"] = f"{program_name}, {university}".strip(", ")

    return data


def save_data(data):
    """Save LLM-ready data as JSON."""

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False,
        )


def load_data():
    """Load the prepared LLM input file."""

    with OUTPUT_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def main():
    data = clean_data()
    save_data(data)

    print(f"Prepared {len(data)} records for LLM cleaning.")
    print(f"Saved to {OUTPUT_FILE}")


if __name__ == "__main__":  # pragma: no cover
    main()