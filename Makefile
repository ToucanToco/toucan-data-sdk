test:
	flake8 toucan_data_sdk tests
	pytest tests --cov-fail-under=100 --cov=toucan_data_sdk --cov-report term-missing

clean:
	find . -name \*.pyc -delete
	find . -name \*.so -delete
	find . -name __pycache__ -delete
	rm -rf .coverage build dist *.egg-info

build:
	python setup.py sdist bdist_wheel

upload:
	twine upload dist/*
