from celery import Celery
import os

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geotrek.settings')

app = Celery('geotrek')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('geotrek.settings.celery')
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
