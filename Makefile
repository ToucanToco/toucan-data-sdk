.DEFAULT_GOAL := all
isort = isort toucan_data_sdk tests setup.py
black = black toucan_data_sdk tests setup.py

.PHONY: install
install:
	pip install -U setuptools pip
	pip install -e '.[test]'

.PHONY: format
format:
	$(isort)
	$(black)

.PHONY: lint
lint:
	flake8 toucan_data_sdk tests setup.py
	$(isort) --check-only
	$(black) --check

.PHONY: mypy
mypy:
	mypy toucan_data_sdk

.PHONY: test
test:
	pytest --cov-fail-under=100 --cov=toucan_data_sdk --cov-report term-missing

.PHONY: all
all: lint mypy test

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
