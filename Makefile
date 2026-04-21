######################################################################
# YamlDB Makefile
######################################################################

# Variables
PYTHON       := python
PIP          := $(PYTHON) -m pip
PACKAGE_NAME := $(shell basename $(CURDIR))
VERSION_FILE := VERSION
GIT          := git
PYENVVERSION := $(shell pyenv version-name)

.PHONY: help install clean reinstall version test test-cov setup-test uninstall-all

help:
	@echo
	@echo "Makefile for YamlDB:"
	@echo
	@echo "  version       - Display current version from $(VERSION_FILE)"
	@echo "  install       - Install in editable mode for local development"
	@echo "  reinstall     - Clean and reinstall locally"
	@echo "  clean         - Remove build artifacts, cache, and test debris"
	@echo "  test          - Run pytest suite with HTML report"
	@echo "  test-cov      - Run pytest with coverage report"
	@echo "  setup-test    - Install test deps"
	@echo

# --- VERSION MANAGEMENT ---

version:
	@cat $(VERSION_FILE)

# --- DEVELOPMENT & TESTING ---

install:
	$(PIP) install -e .

requirements:
	pip-compile --output-file=requirements.txt pyproject.toml

test:
	pytest -v --html=.report.html
	open .report.html

test-cov:
	pytest --cov=yamldb --cov-report=term-missing tests/

setup-test:
	$(PIP) install pytest pytest-mock pytest-cov pytest-html

# --- CLEANUP & REINSTALL ---

uninstall-all:
	@echo "Searching for installed yamldb packages..."
	@$(PIP) freeze | grep "yamldb" | cut -d'=' -f1 | xargs $(PIP) uninstall -y || echo "No yamldb packages found."

clean:
	@echo "Cleaning artifacts and temporary test plugins..."
	rm -rf build/ dist/ *.egg-info .pytest_cache .coverage .report.html
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf tmp/yamldb-*

reinstall: uninstall-all clean
	@echo "Performing fresh install..."
	$(PIP) install -e .