backlog = 2048
bind = "unix:/tmp/gunicorn-geotrek.sock"
pidfile = "{{ BASE_DIR }}/var/pid/gunicorn-geotrek.pid"
workers = {{ GUNICORN_CONF.app.WORKERS }}
timeout = {{ GUNICORN_CONF.app.TIMEOUT }}
debug = False
