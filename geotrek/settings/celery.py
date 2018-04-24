import os


enable_utc = False
accept_content = ['json']
broker_url = os.getenv('CELERY_BROKER_URL', 'redis://127.0.0.1:6379/0')
task_serializer = 'json'
result_serializer = 'json'
result_expires = 5
task_time_limit = 10800
task_soft_time_limit = 21600
result_backend = 'django-db'
