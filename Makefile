SHELL := /bin/bash
VERBOSITY := 1

help:
	@echo "usage:"
	@echo "	make release -- release to Incuna's pypi"
	@echo "	make test -- run the tests, including flake8 & coverage"
	@echo " make runserver -- launch a basic local server with Django admin access"
	@echo " make migrations -- create any missing migrations"
	@echo " make migrate -- create the database if necessary, then run existing migrations"

release:
	@(git diff --quiet && git diff --cached --quiet) || (echo "You have uncommitted changes - stash or commit your changes"; exit 1)
	@git clean -dxf
	@python setup.py register sdist bdist_wheel upload

test:
	@DJANGO_SETTINGS_MODULE=test_project.settings coverage run test_project/manage.py test groups --verbosity=${VERBOSITY}
	@DJANGO_SETTINGS_MODULE=test_project.settings flake8 .
	@DJANGO_SETTINGS_MODULE=test_project.settings coverage report

runserver:
	@test_project/manage.py runserver

migrations:
	@test_project/manage.py makemigrations

migrate:
	@if [ `psql -t -c "SELECT COUNT(1) FROM pg_catalog.pg_database WHERE datname = 'groups'"` -eq 0 ]; then \
		psql -c "CREATE DATABASE groups"; \
	fi
	@test_project/manage.py migrate
