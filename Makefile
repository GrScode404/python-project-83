install:
	uv sync

dev:
	uv run flask --debug --app page_analyzer:app run

lint:
	uv run ruff check page_analyzer

fixlint:
	uv run ruff check --fix page_analyzer

test:
	uv run pytest

test-coverage:
	uv run pytest --cov=page_analyzer --cov-report=xml:coverage.xml

