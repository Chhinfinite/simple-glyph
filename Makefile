.PHONY: install test lint demo clean

install:
	python -m pip install -e ".[dev]"

test:
	python -m pytest -q

lint:
	ruff check src tests

demo:
	simple-glyph demo --out examples/output

clean:
	rm -rf build dist .pytest_cache .ruff_cache
	find . -name "__pycache__" -type d -prune -exec rm -rf {} +
