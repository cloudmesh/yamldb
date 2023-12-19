UNAME=$(shell uname)
VERSION=`head -1 VERSION`

define banner
	@echo
	@echo "############################################################"
	@echo "# $(1) "
	@echo "############################################################"
endef

.PHONY: dist 

welcome: ## Display welcome message
	$(call banner, "Install ${package}")

source: welcome ## Install the package in source mode
	pip install -e . -U

pip: welcome ## Install the package in pip mode
	pip install -e . -U --config-settings editable_mode=strict

##############################################################################
# CHECK
##############################################################################

flake8: ## Run flake8
	cd ..; flake8 --max-line-length 124 --ignore=E722 $(package)/src/cloudmesh
	cd ..; flake8 --max-line-length 124 --ignore=E722 $(package)/tests

pylint: ## Run pylint
	cd ..; pylint --rcfile=$(package)/.pylintrc  $(package)/src/cloudmesh
	cd ..; pylint --rcfile=$(package)/.pylintrc  --disable=F0010 $(package)/tests

##############################################################################
# CLEAN
##############################################################################

clean: ## Clean the project
	$(call banner, "CLEAN")
	rm -rf *.egg-info
	rm -rf *.eggs
	rm -rf docs/build
	rm -rf build
	rm -rf dist
	rm -rf .tox
	rm -rf .tmp
	find . -type d -name '__pycache__' -exec rm -rf {} +
	pip uninstall ${package} -y

cleanall: ## Clean all the project
	cd ../cloudmesh-common; make clean
	cd ../cloudmesh-cmd5; make clean
	cd ../cloudmesh-sys; make clean
	cd ../cloudmesh-bar; make clean
	cd ../cloudmesh-bumpversion; make clean
	cd ../cloudmesh-vpn; make clean
	cd ../cloudmesh-gpu; make clean
	cd ../cloudmesh-rivanna; make clean
	cd ../cloudmesh-catalog; make clean

##############################################################################
# INFO
##############################################################################

info: ## Display info about the project
	@echo "================================================="
	@git remote show origin
	@echo "================================================="
	@git shortlog -sne --all
	@echo "================================================="

##############################################################################
# TEST
##############################################################################

test: ## Run tests
	pytest -v --html=.report.html
	open .report.html

dtest: ## Run tests with no capture
	pytest -v --capture=no

######################################################################
# PYPI
######################################################################

twine: ## Install twine
	pip install -U twine

dist: ## Build the package 
	pip install -q build
	python -m build
	twine check dist/*

local: welcome dist ## Install the package locally
	pip install dist/*.whl

local-force: ## Install the package locally with force
	pip install dist/*.whl --force-reinstall

patch: clean twine ## Build the package and upload it to testpypi
	$(call banner, "patch")
	pip install -r requirements-dev.txt
	cms bumpversion patch
	@VERSION=$$(cat VERSION); \
		git commit -m "bump version ${VERSION}" .; git push
	pip install -q build
	python -m build
	twine check dist/*
	twine upload --repository testpypi  dist/*

minor: clean ## increase the minor version number
	$(call banner, "minor")
	cms bumpversion minor
	@cat VERSION
	@echo

major: clean ## increase the major version number
	$(call banner, "major")
	cms bumpversion major
	@cat VERSION
	@echo

release: clean ## create a release
	$(call banner, "release")
	git tag "v$(VERSION)"
	git push origin main --tags
	pip install -q build
	python -m build
	twine upload --repository pypi dist/*
	$(call banner, "install")
	@cat VERSION
	@echo

upload: ## Upload the package to pypi
	twine check dist/*
	twine upload dist/*

log: ## Update the ChangeLog
	$(call banner, log)
	gitchangelog | fgrep -v ":dev:" | fgrep -v ":new:" > ChangeLog
	git commit -m "chg: dev: Update ChangeLog" ChangeLog
	git push
