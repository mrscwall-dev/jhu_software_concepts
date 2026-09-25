import json

import pytest

from src import clean


@pytest.fixture
def clean_files(tmp_path, monkeypatch):
    input_file = tmp_path / "applicant_data.json"
    output_file = tmp_path / "llm_input.json"

    sample_data = [
        {
            "program_name": "Computer Science",
            "university": "Johns Hopkins University",
        },
        {
            "program_name": "Data Science",
            "university": "",
        },
    ]

    with input_file.open("w", encoding="utf-8") as file:
        json.dump(sample_data, file)

    monkeypatch.setattr(clean, "INPUT_FILE", input_file)
    monkeypatch.setattr(clean, "OUTPUT_FILE", output_file)

    return output_file


@pytest.mark.db
def test_clean_data(clean_files):
    data = clean.clean_data()

    assert data[0]["program"] == (
        "Computer Science, Johns Hopkins University"
    )
    assert data[1]["program"] == "Data Science"


@pytest.mark.db
def test_save_and_load_data(clean_files):
    data = clean.clean_data()

    clean.save_data(data)

    loaded_data = clean.load_data()

    assert loaded_data == data


@pytest.mark.db
def test_main(clean_files):
    clean.main()

    assert clean_files.exists()

    loaded_data = clean.load_data()

    assert len(loaded_data) == 2