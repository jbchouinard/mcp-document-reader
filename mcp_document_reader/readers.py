"""Document reading functionality for mcp-read-pdf."""

import logging
from pathlib import Path

import ebooklib
import pypdf
from bs4 import BeautifulSoup
from ebooklib import epub

logger = logging.getLogger(__name__)

EPUB_METADATA_KEYS = [
    "title",
    "language",
    "creator",
    "author",
    "publisher",
    "identifier",
    "date",
    "rights",
]


class EPUBReader:
    """Class for reading and processing EPUB files."""

    def __init__(self, epub_path: Path | str):
        """Initialize the EPUB reader with a path to an EPUB file.

        Args:
            epub_path: Path to the EPUB file to read.
        """
        self.epub_path = Path(epub_path)
        if not self.epub_path.exists():
            raise FileNotFoundError(f"EPUB file not found: {self.epub_path}")

        # Try to load the EPUB to validate it's a proper EPUB file
        try:
            self.book = epub.read_epub(str(self.epub_path))
        except Exception as e:
            raise ValueError(f"Invalid EPUB file: {self.epub_path}. Error: {e}") from e

        logger.info(f"Initialized EPUB reader for: {self.epub_path}")

    def _get_html_content(self, item) -> str:
        """Extract text content from HTML.

        Args:
            item: EPUB HTML item.

        Returns:
            Extracted text content.
        """
        content = item.get_content().decode("utf-8")
        soup = BeautifulSoup(content, "html.parser")
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
        # Get text
        text = soup.get_text(separator=" ", strip=True)
        return text

    def get_metadata(self) -> dict[str, str]:
        """Get metadata from the EPUB file.

        Returns:
            Dictionary containing EPUB metadata.
        """
        logger.info(f"Getting metadata from EPUB file: {self.epub_path}")
        metadata = {"filename": self.epub_path.name}

        # Extract standard metadata
        for key in EPUB_METADATA_KEYS:
            value = self.book.get_metadata("DC", key)
            if value:
                # EPUB metadata is typically a list of tuples with attributes
                # We'll just extract the text content for simplicity
                metadata[key] = str(value[0][0] if value and value[0] else "")

        # Count the number of items that are documents
        doc_items = [
            item for item in self.book.get_items() if item.get_type() == ebooklib.ITEM_DOCUMENT
        ]
        metadata["PageCount"] = str(len(doc_items))

        return metadata

    def read_all(self) -> str:
        """Read the EPUB file and return its text content.

        Returns:
            The text content of the EPUB file.
        """
        logger.info(f"Reading EPUB file: {self.epub_path}")
        contents = []

        # Get all HTML items (documents) from the EPUB
        for item in self.book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                contents.append(self._get_html_content(item))

        return "\n\n".join(contents)

    def read_pages(self, pages: list[int]) -> dict[int, str]:
        """Extract specific pages from the EPUB file.

        Args:
            pages: List of page numbers (1-based).

        Returns:
            Dictionary of page numbers and their contents.
        """
        page_contents = {}

        # Get all HTML items (documents) from the EPUB
        doc_items = [
            item for item in self.book.get_items() if item.get_type() == ebooklib.ITEM_DOCUMENT
        ]
        total_pages = len(doc_items)

        for page_number in pages:
            if page_number < 1 or page_number > total_pages:
                continue
            page_text = self._get_html_content(doc_items[page_number - 1])
            page_contents[page_number] = page_text

        return page_contents

    def read_page_range(self, from_page: int, to_page: int) -> dict[int, str]:
        """Extract range of pages from the EPUB file.

        Args:
            from_page: The starting page number (1-based).
            to_page: The ending page number (1-based).

        Returns:
            Dictionary of page numbers and their contents.
        """
        return self.read_pages(list(range(from_page, to_page + 1)))

    def read_all_pages(self) -> dict[int, str]:
        """Read all pages from the EPUB file."""
        return self.read_page_range(0, 10000)

    def search(self, terms: list[str] | str) -> dict[int, list[str]]:
        """Search for terms in the EPUB file and return pages containing them.

        Args:
            terms: A list of search terms or a single search term.

        Returns:
            Dictionary mapping page numbers to lists of matching terms found on that page.
        """
        logger.info(f"Searching EPUB file {self.epub_path} for terms: {terms}")

        # Convert single term to list for consistent processing
        if isinstance(terms, str):
            terms = [terms]

        # Convert all terms to lowercase for case-insensitive search
        terms = [term.lower() for term in terms]

        # Get all pages content
        all_pages = self.read_all_pages()

        # Dictionary to store results: {page_number: [matched_terms]}
        results = {}

        # Search each page for each term
        for page_num, content in all_pages.items():
            page_content_lower = content.lower()

            # Check each term
            matches = []
            for term in terms:
                if term in page_content_lower:
                    matches.append(term)

            # If any matches found, add to results
            if matches:
                results[page_num] = matches

        return results


class PDFReader:
    """Class for reading and processing PDF files."""

    def __init__(self, pdf_path: Path | str):
        """Initialize the PDF reader with a path to a PDF file.

        Args:
            pdf_path: Path to the PDF file to read.
        """
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {self.pdf_path}")

        logger.info(f"Initialized PDF reader for: {self.pdf_path}")

    def get_metadata(self) -> dict[str, str]:
        """Get metadata from the PDF file.

        Returns:
            Dictionary containing PDF metadata.
        """
        logger.info(f"Getting metadata from PDF file: {self.pdf_path}")
        metadata = {"filename": self.pdf_path.name}

        with open(self.pdf_path, "rb") as file:
            reader = pypdf.PdfReader(file)
            if reader.metadata:
                for key, value in reader.metadata.items():
                    # Convert the key to a string without the leading slash
                    clean_key = str(key)
                    if clean_key.startswith("/"):
                        clean_key = clean_key[1:]
                    metadata[clean_key] = str(value)

            # Add page count to metadata
            metadata["PageCount"] = str(len(reader.pages))

        return metadata

    def read_all(self) -> str:
        """Read the PDF file and return its text content.

        Returns:
            The text content of the PDF file.
        """
        logger.info(f"Reading PDF file: {self.pdf_path}")
        contents: list[str] = []

        with open(self.pdf_path, "rb") as file:
            reader = pypdf.PdfReader(file)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                contents.append(page.extract_text())  # pyright: ignore[reportArgumentType]

        return "".join(contents)

    def read_pages(self, pages: list[int]) -> dict[int, str]:
        """Extract specific pages from the PDF file.

        Args:
            pages: List of page numbers (1-based).

        Returns:
            Dictionary of page numbers and their contents.
        """
        page_contents = {}
        with open(self.pdf_path, "rb") as file:
            reader = pypdf.PdfReader(file)
            for page_number in pages:
                if page_number < 1 or page_number > len(reader.pages):
                    continue
                page = reader.pages[page_number - 1]
                page_text = page.extract_text()  # pyright: ignore[reportArgumentType]
                page_contents[page_number] = page_text

        return page_contents

    def read_page_range(self, from_page: int, to_page: int) -> dict[int, str]:
        """Extract page range from the PDF file.

        Args:
            from_page: The starting page number (1-based).
            to_page: The ending page number (1-based).

        Returns:
            Dictionary of page numbers and their contents.
        """
        return self.read_pages(list(range(from_page, to_page + 1)))

    def read_all_pages(self) -> dict[int, str]:
        """Read all pages from the PDF file."""
        return self.read_page_range(0, 10000)

    def search(self, terms: list[str] | str) -> dict[int, list[str]]:
        """Search for terms in the PDF file and return pages containing them.

        Args:
            terms: A list of search terms or a single search term.

        Returns:
            Dictionary mapping page numbers to lists of matching terms found on that page.
        """
        logger.info(f"Searching PDF file {self.pdf_path} for terms: {terms}")

        # Convert single term to list for consistent processing
        if isinstance(terms, str):
            terms = [terms]

        # Convert all terms to lowercase for case-insensitive search
        terms = [term.lower() for term in terms]

        # Get all pages content
        all_pages = self.read_all_pages()

        # Dictionary to store results: {page_number: [matched_terms]}
        results = {}

        # Search each page for each term
        for page_num, content in all_pages.items():
            page_content_lower = content.lower()

            # Check each term
            matches = []
            for term in terms:
                if term in page_content_lower:
                    matches.append(term)

            # If any matches found, add to results
            if matches:
                results[page_num] = matches

        return results
