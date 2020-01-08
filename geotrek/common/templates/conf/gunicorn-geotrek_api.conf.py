backlog = 2048
bind = "unix:/tmp/gunicorn-geotrek_api.sock"
pidfile = "{{ BASE_DIR }}/var/pid/gunicorn-geotrek_api.pid"
workers = {{ GUNICORN_CONF.api.WORKERS }}
timeout = {{ GUNICORN_CONF.api.TIMEOUT }}
debug = False
