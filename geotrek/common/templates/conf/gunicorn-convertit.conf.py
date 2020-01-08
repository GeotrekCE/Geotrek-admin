backlog = 2048
bind = {{ CONVERTIT_CONF.HOST }}:{{ CONVERTIT_CONF.PORT }}
pidfile = "{{ BASE_DIR }}/var/pid/gunicorn-convertit.pid"
workers = {{ GUNICORN_CONF.convertit.WORKERS }}
timeout = {{ GUNICORN_CONF.convertit.TIMEOUT }}
debug = False
