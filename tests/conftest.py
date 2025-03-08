"""Test fixtures for mcp-read-pdf."""

from pathlib import Path

import pytest


@pytest.fixture
def test_data_dir() -> Path:
    """Return the path to the test data directory."""
    return Path(__file__).parent / "data"


@pytest.fixture
def sample_pdf_path(test_data_dir) -> Path:
    """Return the path to a sample PDF file for testing."""
    return test_data_dir / "sample.pdf"
