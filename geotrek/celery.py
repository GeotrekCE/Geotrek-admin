from __future__ import absolute_import

import django
from celery import Celery

django.setup()

app = Celery('geotrek')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('geotrek.settings.celery')
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
