from mcp.server.fastmcp import FastMCP

from mcp_document_reader.readers import EPUBReader, PDFReader

mcp = FastMCP("document-reader")


def format_metadata(metadata: dict[str, str]) -> str:
    return "\n".join([f"{key}: {value}" for key, value in metadata.items()])


def format_pages(pages: dict[int, str]) -> str:
    return "\n".join([f"----- Page {page} -----\n{content}" for page, content in pages.items()])


def format_search_results(results: dict[int, list[str]]) -> str:
    if not results:
        return "No matches found."

    formatted_results = []
    for page, terms in results.items():
        terms_str = ", ".join(terms)
        formatted_results.append(f"The page {page} contains the following terms: {terms_str}")

    return "\n".join(formatted_results)


@mcp.tool()
async def get_epub_metadata(epub_path: str) -> str:
    """Get metadata from an EPUB file.

    Args:
        epub_path: Path to the EPUB file

    Returns:
        Formatted string containing the EPUB metadata
    """
    try:
        reader = EPUBReader(epub_path)
    except FileNotFoundError:
        return f"The file {epub_path} does not exist."

    return format_metadata(reader.get_metadata())


@mcp.tool()
async def read_epub_page_range(epub_path: str, start_page: int, end_page: int) -> str:
    """Read a range of pages from an EPUB file.

    Args:
        epub_path: Path to the EPUB file
        start_page: First page to read (inclusive)
        end_page: Last page to read (inclusive)

    Returns:
        Formatted string containing the content of the specified page range
    """
    try:
        reader = EPUBReader(epub_path)
    except FileNotFoundError:
        return f"The file {epub_path} does not exist."

    return format_pages(reader.read_page_range(start_page, end_page))


@mcp.tool()
async def read_epub_pages(epub_path: str, pages: list[int]) -> str:
    """Read specific pages from an EPUB file.

    Args:
        epub_path: Path to the EPUB file
        pages: List of page numbers to read

    Returns:
        Formatted string containing the content of the specified pages
    """
    try:
        reader = EPUBReader(epub_path)
    except FileNotFoundError:
        return f"The file {epub_path} does not exist."

    return format_pages(reader.read_pages(pages))


@mcp.tool()
async def get_pdf_metadata(pdf_path: str) -> str:
    """Get metadata from a PDF file.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Formatted string containing the PDF metadata
    """
    try:
        reader = PDFReader(pdf_path)
    except FileNotFoundError:
        return f"The file {pdf_path} does not exist."

    return format_metadata(reader.get_metadata())


@mcp.tool()
async def read_pdf_page_range(pdf_path: str, start_page: int, end_page: int) -> str:
    """Read a range of pages from a PDF file.

    Args:
        pdf_path: Path to the PDF file
        start_page: First page to read (inclusive)
        end_page: Last page to read (inclusive)

    Returns:
        Formatted string containing the content of the specified page range
    """
    try:
        reader = PDFReader(pdf_path)
    except FileNotFoundError:
        return f"The file {pdf_path} does not exist."

    return format_pages(reader.read_page_range(start_page, end_page))


@mcp.tool()
async def read_pdf_pages(pdf_path: str, pages: list[int]) -> str:
    """Read specific pages from a PDF file.

    Args:
        pdf_path: Path to the PDF file
        pages: List of page numbers to read

    Returns:
        Formatted string containing the content of the specified pages
    """
    try:
        reader = PDFReader(pdf_path)
    except FileNotFoundError:
        return f"The file {pdf_path} does not exist."

    return format_pages(reader.read_pages(pages))


@mcp.tool()
async def search_pdf(pdf_path: str, terms: str | list[str]) -> str:
    """Search for terms in a PDF file and return pages containing them.

    Args:
        pdf_path: Path to the PDF file
        terms: Search term(s) - either a single term as a string or multiple terms as a
            comma-separated string

    Returns:
        Formatted search results showing page numbers and matching terms
    """
    try:
        reader = PDFReader(pdf_path)
    except FileNotFoundError:
        return f"The file {pdf_path} does not exist."

    # Convert comma-separated string to list if needed
    if isinstance(terms, str) and "," in terms:
        terms = [term.strip() for term in terms.split(",")]

    results = reader.search(terms)
    return format_search_results(results)


@mcp.tool()
async def search_epub(epub_path: str, terms: str | list[str]) -> str:
    """Search for terms in an EPUB file and return pages containing them.

    Args:
        epub_path: Path to the EPUB file
        terms: Search term(s) - either a single term as a string or multiple terms as a
            comma-separated string

    Returns:
        Formatted search results showing page numbers and matching terms
    """
    try:
        reader = EPUBReader(epub_path)
    except FileNotFoundError:
        return f"The file {epub_path} does not exist."
    except ValueError as e:
        return f"Error reading EPUB file: {e}"

    # Convert comma-separated string to list if needed
    if isinstance(terms, str) and "," in terms:
        terms = [term.strip() for term in terms.split(",")]

    results = reader.search(terms)
    return format_search_results(results)


def run_server():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    run_server()
