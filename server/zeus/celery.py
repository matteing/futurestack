from __future__ import absolute_import, unicode_literals

import os
from celery import Celery

# set the default Django settings module for the 'celery' program
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "zeus.settings")

app = Celery("zeus")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")


app.conf.beat_schedule = {}

app.conf.beat_scheduler = "django_celery_beat.schedulers:DatabaseScheduler"
app.conf.task_default_queue = "zeus"

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS, force=True)
