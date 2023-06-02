.PHONY: tox
tox:
	rm -rf .tox
	tox -p auto

.PHONY: test
test:
	pytest --cov --cov-config=./tests/.coveragerc --cov-report=term -n auto --e2e tests
