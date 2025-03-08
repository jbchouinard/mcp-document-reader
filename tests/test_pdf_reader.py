"""Tests for the PDF reader module."""

import pypdf
import pytest

from mcp_document_reader.readers import PDFReader


def test_pdf_reader_init_file_not_found():
    """Test that PDFReader raises FileNotFoundError when file doesn't exist."""
    with pytest.raises(FileNotFoundError):
        PDFReader("nonexistent.pdf")


def test_pdf_reader_read_all(tmp_path, monkeypatch):
    """Test that PDFReader.read_all() returns content."""
    # Create a mock PDF file
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_text("Mock PDF content")

    # Mock the PdfReader class
    class MockPage:
        def extract_text(self):
            return "Mock PDF content"

    class MockPdfReader:
        def __init__(self, stream):
            self.pages = [MockPage(), MockPage()]
            self.metadata = {}

    monkeypatch.setattr(pypdf, "PdfReader", MockPdfReader)

    reader = PDFReader(pdf_path)
    content = reader.read_all()

    assert isinstance(content, str)
    assert "Mock PDF content" in content


def test_pdf_reader_get_metadata(tmp_path, monkeypatch):
    """Test that PDFReader.get_metadata() returns metadata."""
    # Create a mock PDF file
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_text("Mock PDF content")

    # Mock the PdfReader class
    class MockPdfReader:
        def __init__(self, stream):
            self.pages = [1, 2, 3]  # Just need a list with a length
            self.metadata = {"/Title": "Test PDF", "/Author": "Test Author"}

    monkeypatch.setattr(pypdf, "PdfReader", MockPdfReader)

    reader = PDFReader(pdf_path)
    metadata = reader.get_metadata()

    assert isinstance(metadata, dict)
    assert metadata["filename"] == pdf_path.name
    assert metadata["Title"] == "Test PDF"
    assert metadata["Author"] == "Test Author"
    assert metadata["PageCount"] == "3"


def test_pdf_reader_read_pages(tmp_path, monkeypatch):
    """Test that PDFReader.read_pages() returns page contents."""
    # Create a mock PDF file
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_text("Mock PDF content")

    # Mock the PdfReader class
    class MockPage:
        def __init__(self, page_num):
            self.page_num = page_num

        def extract_text(self):
            return f"Page {self.page_num} content"

    class MockPdfReader:
        def __init__(self, stream):
            self.pages = [MockPage(i) for i in range(1, 6)]

    monkeypatch.setattr(pypdf, "PdfReader", MockPdfReader)

    reader = PDFReader(pdf_path)
    pages = reader.read_page_range(2, 4)

    assert isinstance(pages, dict)
    assert len(pages) == 3  # Pages 2, 3, 4
    assert pages[2] == "Page 2 content"
    assert pages[3] == "Page 3 content"
    assert pages[4] == "Page 4 content"


def test_pdf_reader_read_all_pages(tmp_path, monkeypatch):
    """Test that PDFReader.read_all_pages() returns all page contents."""
    # Create a mock PDF file
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_text("Mock PDF content")

    # Mock the PdfReader class
    class MockPage:
        def __init__(self, page_num):
            self.page_num = page_num

        def extract_text(self):
            return f"Page {self.page_num} content"

    class MockPdfReader:
        def __init__(self, stream):
            self.pages = [MockPage(i) for i in range(1, 6)]

    monkeypatch.setattr(pypdf, "PdfReader", MockPdfReader)

    reader = PDFReader(pdf_path)
    pages = reader.read_all_pages()

    assert isinstance(pages, dict)
    assert len(pages) == 5  # All 5 pages
    for i in range(1, 6):
        assert pages[i] == f"Page {i} content"


def test_pdf_reader_search_single_term(tmp_path, monkeypatch):
    """Test that PDFReader.search() finds pages containing a single search term."""
    # Create a mock PDF file
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_text("Mock PDF content")

    # Mock the PdfReader class
    class MockPage:
        def __init__(self, page_num):
            self.page_num = page_num

        def extract_text(self):
            # Page 2 and 4 contain the word "search"
            if self.page_num in [2, 4]:
                return f"Page {self.page_num} content with search term"
            return f"Page {self.page_num} content"

    class MockPdfReader:
        def __init__(self, stream):
            self.pages = [MockPage(i) for i in range(1, 6)]

    monkeypatch.setattr(pypdf, "PdfReader", MockPdfReader)

    reader = PDFReader(pdf_path)
    results = reader.search("search")

    assert isinstance(results, dict)
    assert len(results) == 2  # Only pages 2 and 4 contain the term
    assert 2 in results
    assert 4 in results
    assert results[2] == ["search"]
    assert results[4] == ["search"]


def test_pdf_reader_search_multiple_terms(tmp_path, monkeypatch):
    """Test that PDFReader.search() finds pages containing multiple search terms."""
    # Create a mock PDF file
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_text("Mock PDF content")

    # Mock the PdfReader class
    class MockPage:
        def __init__(self, page_num):
            self.page_num = page_num

        def extract_text(self):
            # Page 1: no search terms
            # Page 2: contains "term1"
            # Page 3: contains "term2"
            # Page 4: contains both "term1" and "term2"
            # Page 5: no search terms
            if self.page_num == 2:
                return f"Page {self.page_num} content with term1"
            elif self.page_num == 3:
                return f"Page {self.page_num} content with term2"
            elif self.page_num == 4:
                return f"Page {self.page_num} content with term1 and term2"
            return f"Page {self.page_num} content"

    class MockPdfReader:
        def __init__(self, stream):
            self.pages = [MockPage(i) for i in range(1, 6)]

    monkeypatch.setattr(pypdf, "PdfReader", MockPdfReader)

    reader = PDFReader(pdf_path)
    results = reader.search(["term1", "term2"])

    assert isinstance(results, dict)
    assert len(results) == 3  # Pages 2, 3, and 4 contain at least one term
    assert 2 in results
    assert 3 in results
    assert 4 in results
    assert results[2] == ["term1"]
    assert results[3] == ["term2"]
    assert sorted(results[4]) == ["term1", "term2"]


def test_pdf_reader_search_case_insensitive(tmp_path, monkeypatch):
    """Test that PDFReader.search() is case-insensitive."""
    # Create a mock PDF file
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_text("Mock PDF content")

    # Mock the PdfReader class
    class MockPage:
        def __init__(self, page_num):
            self.page_num = page_num

        def extract_text(self):
            # Page 2 contains the word "SEARCH" in uppercase
            if self.page_num == 2:
                return f"Page {self.page_num} content with SEARCH term"
            return f"Page {self.page_num} content"

    class MockPdfReader:
        def __init__(self, stream):
            self.pages = [MockPage(i) for i in range(1, 6)]

    monkeypatch.setattr(pypdf, "PdfReader", MockPdfReader)

    reader = PDFReader(pdf_path)
    results = reader.search("search")  # Search term in lowercase

    assert isinstance(results, dict)
    assert len(results) == 1  # Only page 2 contains the term
    assert 2 in results
    assert results[2] == ["search"]
