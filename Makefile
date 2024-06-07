.PHONY: clean clean-build clean-pyc clean-test coverage dist docs help install lint lint/flake8 lint/black lint/mypy
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -rf .tox/
	rm -rf .coverage
	rm -rf .benchmarks
	rm -rf .mypy_cache 
	rm -fr htmlcov/
	rm -fr .pytest_cache
	rm -f  0*-*.expanded  0*-*.yaml

lint/flake8: ## check style with flake8
	flake8 --ignore E203,W503 --max-line-length 120 sh_doctest tests

lint/black: ## check style with black
	black --check sh_doctest tests

lint/mypy:
	mypy --install-types sh_doctest

lint: lint/flake8 lint/black lint/mypy ## check style

# test: ## run tests quickly with the default Python
# 	pytest --doctest-continue-on-failure --doctest-glob '*.txt'
test: ## run tests quickly with the default Python
	pytest  --pdb  -v -v -v --doctest-glob '*.txt'

test-all: ## run tests on every Python version with tox
	tox

coverage: ## check code coverage quickly with the default Python
	coverage run --source sh_doctest -m pytest
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

release: dist ## package and upload a release
	twine upload dist/*

dist: clean ## builds source and wheel package
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

install: clean ## install the package to the active Python's site-packages
	python setup.py install
