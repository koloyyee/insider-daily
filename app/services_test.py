"""Tests for app.services — pure functions only, no external dependencies."""

from app.services import filing_info, extract_title


class MockEntry:
    """Emulates the shape of an RSS feed entry used by filing_info()."""
    def __init__(self, title: str, summary: str, link: str, updated: str):
        self.title = title
        self.summary = summary
        self.link = link
        self.updated = updated


def test_extract_title():
    result = extract_title("4 - Atlas Lithium Corp (0001540684) (Issuer)")
    assert result == " Atlas Lithium Corp "


def test_extract_title_no_issuer_suffix():
    result = extract_title("4 - Apple Inc. (0000320193) (Issuer)")
    assert result == " Apple Inc. "


def test_filing_info_standard():
    entry = MockEntry(
        title="4 - NVIDIA CORP (0001045810) (Issuer)",
        summary="2026-06-18\nAccession No: 0001140361-26-025796\n...",
        link="https://www.sec.gov/Archives/edgar/data/1045810/000114036126025796/0001140361-26-025796-index.htm",
        updated="2026-06-18T21:59:08-04:00",
    )
    result = filing_info(entry)
    assert result["date"] == "2026-06-18"
    assert result["cik"] == "0001045810"
    assert result["acc_no"] == "0001140361-26-025796"
    assert result["title"] == "4 - NVIDIA CORP (0001045810) (Issuer)"
    assert "sec.gov" in result["link"]
    assert result["updated"] == "2026-06-18T21:59:08-04:00"


def test_filing_info_empty_summary():
    """Edge case: summary is empty string, regex finds nothing."""
    entry = MockEntry(
        title="4 - Unknown Corp (0000000001) (Issuer)",
        summary="",
        link="",
        updated="",
    )
    result = filing_info(entry)
    assert result["date"] == ""
    assert result["acc_no"] == ""


def test_filing_info_title_format():
    """Handle CIK extraction with different spacing/formatting."""
    entry = MockEntry(
        title="4 - EBAY INC (0001065088) (Issuer)",
        summary="2026-06-18\nAccession No: 0001065088-26-000161\n...",
        link="https://www.sec.gov/...",
        updated="2026-06-18T21:04:31-04:00",
    )
    result = filing_info(entry)
    assert result["cik"] == "0001065088"
    assert result["date"] == "2026-06-18"
    assert result["acc_no"] == "0001065088-26-000161"
