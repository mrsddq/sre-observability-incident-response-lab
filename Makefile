.PHONY: test validate run

test:
	python -m unittest discover -s tests

validate: test
	python synthetics/check_http.py --dry-run

run:
	python services/api/app.py
