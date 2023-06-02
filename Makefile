.PHONY: tox
tox:
	rm -rf .tox
	tox -p auto

.PHONY: test
test:
	pytest --cov --cov-config=./tests/.coveragerc --cov-report=term -n auto --e2e tests

.PHONY: reformat
reformat:
	ruff check . --fix
	black .

.PHONY: lint
lint:
	ruff . --no-fix
	black . --check
