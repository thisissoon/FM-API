#
# Makefile
#

.PHONY: clean-pyc clean-build docs

help:
	@echo "clean - cleans up pyc files and build directories"
	@echo "clean-build - cleans build directories"
	@echo "clean-pyc - cleans pyc files"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "sdist - creates a distribution and lists contents"
	@echo "test - runs test suite"

clean: clean-build clean-pyc

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

docs:
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	open docs/_build/html/index.html

develop:
	bash -c 'pip install -e .[develop] --process-dependency-links'

test:
	python setup.py test
	coveralls

sdist: clean
	python setup.py sdist
	find dist -type f -exec ls {} \; | xargs tar -ztvf $$1
