.PHONY: lint test

lint:
	ruff check --fix .
	ruff format .

test:
	poetry run pytest
