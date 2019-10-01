.DEFAULT_GOAL := all

.PHONY: install
install:
	pip install -U setuptools pip
	pip install -e '.[test]'

.PHONY: format
format:
	isort -rc -w 100 toucan_data_sdk tests
	black -S -l 100 --target-version py36 toucan_data_sdk tests

.PHONY: lint
lint:
	flake8 toucan_data_sdk tests
	isort -c -rc -w 100 toucan_data_sdk tests
	black -S -l 100 --target-version py36 --check toucan_data_sdk tests

.PHONY: mypy
mypy:
	mypy --ignore-missing-imports --no-strict-optional toucan_data_sdk

.PHONY: test
test:
	pytest --cov-fail-under=100 --cov=toucan_data_sdk --cov-report term-missing

.PHONY: all
all: test mypy lint

.PHONY: clean
clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -rf .coverage build dist *.egg-info .pytest_cache .mypy_cache

.PHONY: build
build:
	python setup.py sdist bdist_wheel

.PHONY: upload
upload:
	twine upload dist/*
