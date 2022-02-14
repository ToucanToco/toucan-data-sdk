.DEFAULT_GOAL := all
black = poetry run black toucan_data_sdk tests
isort = poetry run isort toucan_data_sdk tests

.PHONY: install
install:
	poetry install
	poetry run pre-commit install

.PHONY: format
format:
	$(black)
	$(isort)

.PHONY: lint
lint:
	poetry run flake8 toucan_data_sdk tests
	$(black) --diff --check
	$(isort) --check-only

.PHONY: mypy
mypy:
	poetry run mypy .

.PHONY: test
test:
	poetry run pytest --cov=toucan_data_sdk --cov-report xml --cov-report term-missing

.PHONY: all
all: lint mypy test

.PHONY: clean
clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -rf .coverage coverage.xml build dist *.egg-info .pytest_cache .mypy_cache

.PHONY: build
build:
	poetry build

.PHONY: upload
upload:
	poetry publish
