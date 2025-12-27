from pathlib import Path
import builtins
import types
import csv

import pytest

from email_me_anything.csvutils import (
    read_csv,
    convert_row_to_dict,
    select_random_row,
)


def test_convert_row_to_dict_with_headers_exact():
    row = ["Alice", "42", "NYC"]
    headers = ["name", "age", "city"]
    assert convert_row_to_dict(row, headers) == {
        "name": "Alice",
        "age": "42",
        "city": "NYC",
    }


def test_convert_row_to_dict_with_headers_missing_values():
    row = ["Bob", "30"]
    headers = ["name", "age", "city"]
    assert convert_row_to_dict(row, headers) == {
        "name": "Bob",
        "age": "30",
        "city": "",
    }


def test_convert_row_to_dict_without_headers():
    row = ["Charlie", "35", "LA"]
    assert convert_row_to_dict(row) == {"col0": "Charlie", "col1": "35", "col2": "LA"}


def test_read_csv_success(tmp_path: Path):
    p = tmp_path / "data.csv"
    p.write_text("a,b\n1,2\n", encoding="utf-8")
    rows = read_csv(p)
    assert rows == [["a", "b"], ["1", "2"]]


def test_read_csv_missing_file_returns_none(tmp_path: Path):
    missing = tmp_path / "none.csv"
    assert read_csv(missing) is None


def test_select_random_row_with_single_data_row(sample_csv: Path):
    # With only one data row, selection is deterministic
    result = select_random_row(sample_csv)
    assert result == {"name": "Ada", "quote": "Imagination is intelligence with an erection"}


def test_select_random_row_header_only_returns_none(header_only_csv: Path):
    assert select_random_row(header_only_csv) is None


def test_select_random_row_file_not_found_returns_false(tmp_path: Path):
    missing = tmp_path / "missing.csv"
    assert select_random_row(missing) is False
