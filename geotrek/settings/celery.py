import os

enable_utc = False
accept_content = ['json']
broker_url = 'redis://{}:{}/{}'.format(os.getenv('REDIS_HOST'),
                                       os.getenv('REDIS_PORT'),
                                       os.getenv('REDIS_DB'),)
task_serializer = 'json'
result_serializer = 'json'
result_expires = 5
task_time_limit = 10800
task_soft_time_limit = 21600
result_backend = 'django-db'
