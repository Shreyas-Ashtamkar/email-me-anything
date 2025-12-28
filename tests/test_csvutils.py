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


def test_convert_row_to_dict_empty_row_with_headers():
    """Test converting an empty row with headers"""
    row = []
    headers = ["name", "age", "city"]
    assert convert_row_to_dict(row, headers) == {
        "name": "",
        "age": "",
        "city": "",
    }


def test_convert_row_to_dict_empty_row_without_headers():
    """Test converting an empty row without headers"""
    row = []
    assert convert_row_to_dict(row) == {}


def test_read_csv_success(tmp_path: Path):
    p = tmp_path / "data.csv"
    p.write_text("a,b\n1,2\n", encoding="utf-8")
    rows = read_csv(p)
    assert rows == [["a", "b"], ["1", "2"]]


def test_read_csv_missing_file_returns_none(tmp_path: Path):
    missing = tmp_path / "none.csv"
    assert read_csv(missing) is None


def test_read_csv_empty_file(tmp_path: Path):
    """Test reading an empty CSV file"""
    p = tmp_path / "empty.csv"
    p.write_text("", encoding="utf-8")
    rows = read_csv(p)
    assert rows == []


def test_read_csv_with_empty_lines(tmp_path: Path):
    """Test reading CSV with empty lines"""
    p = tmp_path / "data.csv"
    p.write_text("a,b\n1,2\n\n3,4\n", encoding="utf-8")
    rows = read_csv(p)
    assert rows == [["a", "b"], ["1", "2"], [], ["3", "4"]]


def test_read_csv_with_special_characters(tmp_path: Path):
    """Test reading CSV with special characters and Unicode"""
    p = tmp_path / "data.csv"
    p.write_text("name,quote\nAda,Imagination is intelligence with an erection\n", encoding="utf-8")
    rows = read_csv(p)
    assert rows == [["name", "quote"], ["Ada", "Imagination is intelligence with an erection"]]


def test_select_random_row_with_single_data_row(sample_csv: Path):
    # With only one data row, selection is deterministic
    result = select_random_row(sample_csv)
    assert result == {"name": "Ada", "quote": "Imagination is intelligence with an erection"}


def test_select_random_row_header_only_returns_none(header_only_csv: Path):
    assert select_random_row(header_only_csv) is None


def test_select_random_row_file_not_found_returns_false(tmp_path: Path):
    missing = tmp_path / "missing.csv"
    assert select_random_row(missing) is False


def test_select_random_row_with_multiple_rows(tmp_path: Path):
    """Test that select_random_row can select from multiple rows"""
    p = tmp_path / "multi.csv"
    p.write_text("id,value\n1,A\n2,B\n3,C\n4,D\n5,E\n", encoding="utf-8")
    
    # Run multiple times to check we get different values
    results = set()
    for _ in range(20):
        result = select_random_row(p)
        results.add(frozenset(result.items()))
    
    # Should have selected from multiple rows
    assert len(results) >= 2


def test_select_random_row_skip_header_false(tmp_path: Path):
    """Test select_random_row with skip_header=False"""
    p = tmp_path / "data.csv"
    p.write_text("a,b\n1,2\n3,4\n", encoding="utf-8")
    
    result = select_random_row(p, skip_header=False)
    # Should be one of the rows, including the header
    assert result["col0"] in ["a", "1", "3"]
