.PHONY: install build test clean

install:
	pip install -e ".[dev]"

build:
	babysafety compile

test:
	python -m pytest tests/ -v

clean:
	rm -f data/compiled/ingredients.json data/compiled/alias_index.json
