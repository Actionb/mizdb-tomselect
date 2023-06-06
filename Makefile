.PHONY: tox
tox:
	rm -rf .tox
	tox -p auto

.PHONY: test
test:
	pytest --cov --cov-config=./tests/.coveragerc --cov-report=term-missing -n auto --e2e tests

.PHONY: reformat
reformat:
	ruff check . --fix
	black .
	standard src/ --fix

.PHONY: lint
lint:
	ruff . --no-fix
	black . --check
	standard src/
