test:
	PYTHONPATH=. pytest tests

clean:
	find . -name '*.pyc' -o -name '*.so' -delete
	find . -name __pycache__ -delete
	rm -rf .coverage build dist UNKNOWN.egg-info
