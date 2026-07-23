import pytest
from app.etl.extract import extract_text


def test_extract_plain_text():
    contents = b"Hello, world!"
    result = extract_text(contents, "sample.txt")
    assert result == "Hello, world!"


def test_extract_unsupported_encoding():
    contents = "Cześć".encode("latin-1")
    result = extract_text(contents, "sample.txt")
    assert isinstance(result, str)


def test_extract_empty_file():
    result = extract_text(b"", "empty.txt")
    assert result == ""
