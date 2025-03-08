"""Tests for the EPUB reader module."""

from pathlib import Path

import ebooklib
import pytest

from mcp_document_reader.readers import EPUBReader


def test_epub_reader_init_file_not_found():
    """Test that EPUBReader raises FileNotFoundError when file doesn't exist."""
    with pytest.raises(FileNotFoundError):
        EPUBReader("nonexistent.epub")


def test_epub_reader_init_invalid_file(tmp_path):
    """Test that EPUBReader raises ValueError when file is not a valid EPUB."""
    # Create a mock file that's not a valid EPUB
    epub_path = tmp_path / "test.epub"
    epub_path.write_text("This is not a valid EPUB file")

    with pytest.raises(ValueError):
        EPUBReader(epub_path)


def test_epub_reader_get_metadata(monkeypatch, tmp_path):
    """Test that EPUBReader.get_metadata() returns metadata."""
    # This test requires mocking since we can't easily create a valid EPUB file
    # in a test environment without additional dependencies

    class MockEpub:
        def get_metadata(self, namespace, name):
            if name == "title":
                return [("Test Book", {})]
            elif name == "creator":
                return [("Test Author", {})]
            return []

        def get_items(self):
            return [MockItem(), MockItem()]

    class MockItem:
        def get_type(self):
            return ebooklib.ITEM_DOCUMENT

    class MockEbooklib:
        ITEM_DOCUMENT = "ITEM_DOCUMENT"

    # Create a mock file
    epub_path = tmp_path / "test.epub"
    epub_path.write_text("Mock EPUB content")

    # Create a mock instance
    mock_epub = MockEpub()
    # Mock the epub module
    monkeypatch.setattr("ebooklib.epub.read_epub", lambda path: mock_epub)
    monkeypatch.setattr("mcp_document_reader.readers.ebooklib.ITEM_DOCUMENT", "ITEM_DOCUMENT")

    reader = EPUBReader(epub_path)
    metadata = reader.get_metadata()

    assert isinstance(metadata, dict)
    assert metadata["filename"] == epub_path.name
    assert metadata["title"] == "Test Book"
    assert metadata["creator"] == "Test Author"
    assert metadata["PageCount"] == "2"


def test_epub_reader_read_all(monkeypatch, tmp_path):
    """Test that EPUBReader.read_all() returns content."""

    # Mock classes
    class MockEpub:
        def get_items(self):
            return [MockItem("Content 1"), MockItem("Content 2")]

    class MockItem:
        def __init__(self, content):
            self.content = content

        def get_type(self):
            return ebooklib.ITEM_DOCUMENT

        def get_content(self):
            return f"<html><body>{self.content}</body></html>".encode("utf-8")

    class MockEbooklib:
        ITEM_DOCUMENT = "ITEM_DOCUMENT"

    class MockBeautifulSoup:
        def __init__(self, content, parser):
            self.content = content

        def __call__(self, tags):
            return []

        def get_text(self, separator=" ", strip=True):
            # Extract content from between body tags
            import re

            match = re.search(r"<body>(.*?)</body>", self.content)
            return match.group(1) if match else ""

    # Create a mock file
    epub_path = tmp_path / "test.epub"
    epub_path.write_text("Mock EPUB content")

    # Create a mock instance
    mock_epub = MockEpub()
    # Mock the modules
    monkeypatch.setattr("ebooklib.epub.read_epub", lambda path: mock_epub)
    monkeypatch.setattr("mcp_document_reader.readers.ebooklib.ITEM_DOCUMENT", "ITEM_DOCUMENT")
    monkeypatch.setattr("mcp_document_reader.readers.BeautifulSoup", MockBeautifulSoup)

    # Patch the EPUBReader class to use our mock
    def mock_init(self, path):
        self.epub_path = Path(path)
        self.book = mock_epub

    monkeypatch.setattr("mcp_document_reader.readers.EPUBReader.__init__", mock_init)

    reader = EPUBReader(epub_path)
    content = reader.read_all()

    assert isinstance(content, str)
    assert "Content 1" in content
    assert "Content 2" in content


def test_epub_reader_read_pages(monkeypatch, tmp_path):
    """Test that EPUBReader.read_pages() returns page contents."""

    # Mock classes
    class MockEpub:
        def get_items(self):
            return []

        def get_metadata(self, namespace, name):
            return []

    class MockItem:
        def __init__(self, content):
            self.content = content

        def get_type(self):
            return ebooklib.ITEM_DOCUMENT

        def get_content(self):
            return f"<html><body>{self.content}</body></html>".encode("utf-8")

    class MockEbooklib:
        ITEM_DOCUMENT = "ITEM_DOCUMENT"

    class MockBeautifulSoup:
        def __init__(self, content, parser):
            self.content = content

        def __call__(self, tags):
            return []

        def get_text(self, separator=" ", strip=True):
            # Extract content from between body tags
            import re

            match = re.search(r"<body>(.*?)</body>", self.content)
            return match.group(1) if match else ""

    # Create a mock file
    epub_path = tmp_path / "test.epub"
    epub_path.write_text("Mock EPUB content")

    # Create mock items
    mock_items = [MockItem(f"Page {i + 1} content") for i in range(5)]

    # Create a mock instance
    mock_epub = MockEpub()
    # Replace the get_items method on the instance
    mock_epub.get_items = lambda: mock_items

    # Mock the modules
    monkeypatch.setattr("ebooklib.epub.read_epub", lambda path: mock_epub)
    monkeypatch.setattr("mcp_document_reader.readers.ebooklib.ITEM_DOCUMENT", "ITEM_DOCUMENT")
    monkeypatch.setattr("mcp_document_reader.readers.BeautifulSoup", MockBeautifulSoup)

    # Patch the EPUBReader class to use our mock
    def mock_init(self, path):
        self.epub_path = Path(path)
        self.book = mock_epub

    monkeypatch.setattr("mcp_document_reader.readers.EPUBReader.__init__", mock_init)

    reader = EPUBReader(epub_path)
    pages = reader.read_page_range(2, 4)

    assert isinstance(pages, dict)
    assert len(pages) == 3  # Pages 2, 3, 4
    assert pages[2] == "Page 2 content"
    assert pages[3] == "Page 3 content"
    assert pages[4] == "Page 4 content"


def test_epub_reader_read_all_pages(monkeypatch, tmp_path):
    """Test that EPUBReader.read_all_pages() returns all page contents."""

    # Mock classes
    class MockEpub:
        def get_items(self):
            return []

        def get_metadata(self, namespace, name):
            return []

    class MockItem:
        def __init__(self, content):
            self.content = content

        def get_type(self):
            return ebooklib.ITEM_DOCUMENT

        def get_content(self):
            return f"<html><body>{self.content}</body></html>".encode("utf-8")

    # Create a mock file
    epub_path = tmp_path / "test.epub"
    epub_path.write_text("Mock EPUB content")

    # Create mock items
    mock_items = [MockItem(f"Page {i + 1} content") for i in range(5)]

    # Create a mock instance
    mock_epub = MockEpub()
    # Replace the get_items method on the instance
    mock_epub.get_items = lambda: mock_items

    # Mock the modules
    monkeypatch.setattr("ebooklib.epub.read_epub", lambda path: mock_epub)
    monkeypatch.setattr("mcp_document_reader.readers.ebooklib.ITEM_DOCUMENT", "ITEM_DOCUMENT")

    # Mock BeautifulSoup to return the content directly
    class MockBeautifulSoup:
        def __init__(self, content, parser):
            self.content = content

        def __call__(self, tags):
            return []

        def get_text(self, separator=" ", strip=True):
            import re

            match = re.search(r"<body>(.*?)</body>", self.content)
            return match.group(1) if match else ""

    monkeypatch.setattr("mcp_document_reader.readers.BeautifulSoup", MockBeautifulSoup)

    # Patch the EPUBReader class to use our mock
    def mock_init(self, path):
        self.epub_path = Path(path)
        self.book = mock_epub

    monkeypatch.setattr("mcp_document_reader.readers.EPUBReader.__init__", mock_init)

    reader = EPUBReader(epub_path)
    pages = reader.read_all_pages()

    assert isinstance(pages, dict)
    assert len(pages) == 5  # All 5 pages
    for i in range(1, 6):
        assert pages[i] == f"Page {i} content"


def test_epub_reader_search_single_term(monkeypatch, tmp_path):
    """Test that EPUBReader.search() finds pages containing a single search term."""

    # Mock classes
    class MockEpub:
        def get_items(self):
            return []

        def get_metadata(self, namespace, name):
            return []

    class MockItem:
        def __init__(self, content):
            self.content = content

        def get_type(self):
            return ebooklib.ITEM_DOCUMENT

        def get_content(self):
            return f"<html><body>{self.content}</body></html>".encode("utf-8")

    # Create a mock file
    epub_path = tmp_path / "test.epub"
    epub_path.write_text("Mock EPUB content")

    # Create mock items with search term in pages 2 and 4
    mock_items = []
    for i in range(5):
        if i + 1 in [2, 4]:
            mock_items.append(MockItem(f"Page {i + 1} content with search term"))
        else:
            mock_items.append(MockItem(f"Page {i + 1} content"))

    # Create a mock instance
    mock_epub = MockEpub()
    # Replace the get_items method on the instance
    mock_epub.get_items = lambda: mock_items

    # Mock the modules
    monkeypatch.setattr("ebooklib.epub.read_epub", lambda path: mock_epub)
    monkeypatch.setattr("mcp_document_reader.readers.ebooklib.ITEM_DOCUMENT", "ITEM_DOCUMENT")

    # Mock BeautifulSoup to return the content directly
    class MockBeautifulSoup:
        def __init__(self, content, parser):
            self.content = content

        def __call__(self, tags):
            return []

        def get_text(self, separator=" ", strip=True):
            import re

            match = re.search(r"<body>(.*?)</body>", self.content)
            return match.group(1) if match else ""

    monkeypatch.setattr("mcp_document_reader.readers.BeautifulSoup", MockBeautifulSoup)

    # Patch the EPUBReader class to use our mock
    def mock_init(self, path):
        self.epub_path = Path(path)
        self.book = mock_epub

    monkeypatch.setattr("mcp_document_reader.readers.EPUBReader.__init__", mock_init)

    reader = EPUBReader(epub_path)
    results = reader.search("search")

    assert isinstance(results, dict)
    assert len(results) == 2  # Only pages 2 and 4 contain the term
    assert 2 in results
    assert 4 in results
    assert results[2] == ["search"]
    assert results[4] == ["search"]


def test_epub_reader_search_multiple_terms(monkeypatch, tmp_path):
    """Test that EPUBReader.search() finds pages containing multiple search terms."""

    # Mock classes
    class MockEpub:
        def get_items(self):
            return []

        def get_metadata(self, namespace, name):
            return []

    class MockItem:
        def __init__(self, content):
            self.content = content

        def get_type(self):
            return ebooklib.ITEM_DOCUMENT

        def get_content(self):
            return f"<html><body>{self.content}</body></html>".encode("utf-8")

    # Create a mock file
    epub_path = tmp_path / "test.epub"
    epub_path.write_text("Mock EPUB content")

    # Create mock items with different search terms
    # Page 1: no search terms
    # Page 2: contains "term1"
    # Page 3: contains "term2"
    # Page 4: contains both "term1" and "term2"
    # Page 5: no search terms
    mock_items = [
        MockItem("Page 1 content"),
        MockItem("Page 2 content with term1"),
        MockItem("Page 3 content with term2"),
        MockItem("Page 4 content with term1 and term2"),
        MockItem("Page 5 content"),
    ]

    # Create a mock instance
    mock_epub = MockEpub()
    # Replace the get_items method on the instance
    mock_epub.get_items = lambda: mock_items

    # Mock the modules
    monkeypatch.setattr("ebooklib.epub.read_epub", lambda path: mock_epub)
    monkeypatch.setattr("mcp_document_reader.readers.ebooklib.ITEM_DOCUMENT", "ITEM_DOCUMENT")

    # Mock BeautifulSoup to return the content directly
    class MockBeautifulSoup:
        def __init__(self, content, parser):
            self.content = content

        def __call__(self, tags):
            return []

        def get_text(self, separator=" ", strip=True):
            import re

            match = re.search(r"<body>(.*?)</body>", self.content)
            return match.group(1) if match else ""

    monkeypatch.setattr("mcp_document_reader.readers.BeautifulSoup", MockBeautifulSoup)

    # Patch the EPUBReader class to use our mock
    def mock_init(self, path):
        self.epub_path = Path(path)
        self.book = mock_epub

    monkeypatch.setattr("mcp_document_reader.readers.EPUBReader.__init__", mock_init)

    reader = EPUBReader(epub_path)
    results = reader.search(["term1", "term2"])

    assert isinstance(results, dict)
    assert len(results) == 3  # Pages 2, 3, and 4 contain at least one term
    assert 2 in results
    assert 3 in results
    assert 4 in results
    assert results[2] == ["term1"]
    assert results[3] == ["term2"]
    assert sorted(results[4]) == ["term1", "term2"]


def test_epub_reader_search_case_insensitive(monkeypatch, tmp_path):
    """Test that EPUBReader.search() is case-insensitive."""

    # Mock classes
    class MockEpub:
        def get_items(self):
            return []

        def get_metadata(self, namespace, name):
            return []

    class MockItem:
        def __init__(self, content):
            self.content = content

        def get_type(self):
            return ebooklib.ITEM_DOCUMENT

        def get_content(self):
            return f"<html><body>{self.content}</body></html>".encode("utf-8")

    # Create a mock file
    epub_path = tmp_path / "test.epub"
    epub_path.write_text("Mock EPUB content")

    # Create mock items with uppercase search term in page 2
    mock_items = [
        MockItem("Page 1 content"),
        MockItem("Page 2 content with SEARCH term"),  # Uppercase "SEARCH"
        MockItem("Page 3 content"),
        MockItem("Page 4 content"),
        MockItem("Page 5 content"),
    ]

    # Create a mock instance
    mock_epub = MockEpub()
    # Replace the get_items method on the instance
    mock_epub.get_items = lambda: mock_items

    # Mock the modules
    monkeypatch.setattr("ebooklib.epub.read_epub", lambda path: mock_epub)
    monkeypatch.setattr("mcp_document_reader.readers.ebooklib.ITEM_DOCUMENT", "ITEM_DOCUMENT")

    # Mock BeautifulSoup to return the content directly
    class MockBeautifulSoup:
        def __init__(self, content, parser):
            self.content = content

        def __call__(self, tags):
            return []

        def get_text(self, separator=" ", strip=True):
            import re

            match = re.search(r"<body>(.*?)</body>", self.content)
            return match.group(1) if match else ""

    monkeypatch.setattr("mcp_document_reader.readers.BeautifulSoup", MockBeautifulSoup)

    # Patch the EPUBReader class to use our mock
    def mock_init(self, path):
        self.epub_path = Path(path)
        self.book = mock_epub

    monkeypatch.setattr("mcp_document_reader.readers.EPUBReader.__init__", mock_init)

    reader = EPUBReader(epub_path)
    results = reader.search("search")  # Search term in lowercase

    assert isinstance(results, dict)
    assert len(results) == 1  # Only page 2 contains the term
    assert 2 in results
    assert results[2] == ["search"]
