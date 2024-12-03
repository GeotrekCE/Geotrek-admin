from celery import Celery
import os

from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'geotrek.settings')

app = Celery('geotrek')
app.conf.update(
    enable_utc=False,
    accept_content=['json'],
    broker_url=settings.REDIS_URL,
    task_serializer='json',
    result_serializer='json',
    result_expires=5,
    task_time_limit=10800,
    task_soft_time_limit=21600,
    result_backend='django-db',
)
app.autodiscover_tasks()
