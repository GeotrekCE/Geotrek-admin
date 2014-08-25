
{% set cfg = opts['ms_project'] %}
include:
  - makina-states.projects.{{cfg['api_version']}}.{{cfg['installer']}}.archive

