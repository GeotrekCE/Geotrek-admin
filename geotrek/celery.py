from celery import Celery
import os

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geotrek.settings')

app = Celery('geotrek')
app.conf.update(
    enable_utc=False,
    accept_content=['json'],
    broker_url='redis://{}:{}/{}'.format(os.getenv('REDIS_HOST', 'localhost'),
                                         os.getenv('REDIS_PORT', '6379'),
                                         os.getenv('REDIS_DB', '0'), ),
    task_serializer='json',
    result_serializer='json',
    result_expires=5,
    task_time_limit=10800,
    task_soft_time_limit=21600,
    result_backend='django-db',
)
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
