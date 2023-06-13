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
	standard client/ --fix

.PHONY: lint
lint:
	ruff . --no-fix
	black . --check
	standard client/

.PHONY: build
build:
	npm run build
