.PHONY: setup build check test lint preview release-check

setup:
	uv sync --locked
build:
	uv run --locked dotmemo-mijote build
check: build
	uv run --locked dotmemo-mijote check
test:
	uv run --locked pytest -q
lint:
	uv run --locked ruff check .
	uv run --locked ruff format --check src tests tools/check_repository.py
preview: build
	uv run python -m http.server 8000 --bind 127.0.0.1 --directory build
release-check:
	uv run --locked dotmemo-mijote release-check
