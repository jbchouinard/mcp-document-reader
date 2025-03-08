# mcp-document-reader

A rudimentary [MCP server](https://modelcontextprotocol.io/introduction) for interacting with PDF and EPUB documents.

I use this with [Windsurf IDE by Codeium](https://codeium.com/windsurf), which
only supports MCP tools, not resources.

## Installation

### Requirements

- [Python 3.11+](https://www.python.org/downloads/)
- [Poetry](https://python-poetry.org/docs/)

```bash
# Clone the repository
git clone https://github.com/jbchouinard/mcp-document-reader.git
cd mcp-document-reader
poetry install
```

## Configure MCP Server

Run with poetry:

```json
{
  "mcpServers": {
    "documents": {
      "command": "poetry",
      "args": ["-C", "path/to/mcp-document-reader", "run", "mcp-document-reader"]
    }
  }
}
```

Alternatively, build and install with pip, then run the script directly:

```bash
poetry build
pipx install dist/*.whl
which mcp-document-reader
```

Then use the following config, with the path output by which:

```json
{
  "mcpServers": {
    "documents": {
      "command": "/path/to/mcp-document-reader",
      "args": []
    }
  }
}
```

## Development

### Setup

```bash
# Install dependencies
poetry install
```

### Testing

```bash
poetry run pytest
```

### Linting

```bash
poetry run ruff check --fix .
poetry run ruff format .
```

## License

[MIT](LICENSE)
