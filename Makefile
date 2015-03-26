SHELL := /bin/bash
VERBOSITY := 1

help:
	@echo "usage:"
	@echo "	make release -- release to Incuna's pypi"
	@echo "	make test -- run the tests, including flake8 & coverage"

release:
	@(git diff --quiet && git diff --cached --quiet) || (echo "You have uncommitted changes - stash or commit your changes"; exit 1)
	@git clean -dxf
	@python setup.py register -r incuna sdist bdist_wheel upload -r incuna

test:
	@coverage run groups/tests/run.py --verbosity=${VERBOSITY}
	@flake8 .
	@coverage report --fail-under=100
