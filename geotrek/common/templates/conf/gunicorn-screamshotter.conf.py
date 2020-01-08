backlog = 2048
bind = "{{ SCREAMSHOTTER_CONF.HOST }}:{{ SCREAMSHOTTER_CONF.PORT }}"
pidfile = "{{ BASE_DIR }}/var/pid/gunicorn-screamshotter.pid"
workers = {{ GUNICORN_CONF.screamshotter.WORKERS }}
timeout = {{ GUNICORN_CONF.screamshotter.TIMEOUT }}
debug = False
raw_env = ["LOG_FILE={{ VAR_DIR }}/log/screamshotter.log"]
