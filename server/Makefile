.PHONY: all serve help test clean install collect docker freeze

COMMAND=python3 manage.py
SETTINGS=makerlog.settings
APP=zeus

all: migrate status serve

up:
	parallel  --lb ::: '$(COMMAND) runserver --settings=$(SETTINGS)' 'celery worker -B -E -A $(APP) --loglevel=INFO'

redis:
	redis-server --daemonize yes

serve:
	$(COMMAND) runserver --settings=$(SETTINGS)

migrate:
	$(COMMAND) migrate --settings=$(SETTINGS)

migrations:
	$(COMMAND) makemigrations --settings=$(SETTINGS)

# target: help - Display callable targets.
help:
	@egrep "^# target:" [Mm]akefile

# target: test - calls the "test" django command
test:
	$(COMMAND) test --settings=$(SETTINGS)

# target: coverage, works on mac!
coverage:
	coverage run --rcfile=.coveragerc manage.py test
	coverage html
	open ./htmlcov/index.html
	@echo "Run 'serve' in the 'htmlcov' directory to see interactive coverage reports."

# target: clean - remove all ".pyc" files
clean:
	$(COMMAND) clean_pyc --settings=$(SETTINGS)

# target: update - install (and update) pip requirements
install:
	pip3 install -r requirements.txt

freeze:
	pip freeze > requirements.txt

# target: collect - calls the "collectstatic" django command
collect:
	$(COMMAND) collectstatic --settings=$(SETTINGS) --noinput

# target: testwatch, requires entr
testwatch:
	find . | entr $(COMMAND) test --settings=$(SETTINGS)

# target: status, shows info
status:
	$(COMMAND) status --settings=$(SETTINGS)

# celery configuration for local environments
celery:
	celery worker -B -E -A $(APP) --loglevel=INFO

inspectqueue:
	celery -A $(APP) events

stage:
	git push staging develop:master

deploy:
	git push dokku master

tunnel:
	ssh -R 80:localhost:8000 matteing@serveo.net -o "StrictHostKeyChecking no"

docker:
	python manage.py status && \
	python manage.py migrate && \
	gunicorn --reload --workers 3 --bind 0.0.0.0:8000 -k uvicorn.workers.UvicornWorker makerlog.asgi:application