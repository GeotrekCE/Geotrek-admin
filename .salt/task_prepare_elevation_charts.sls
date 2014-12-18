{% set cfg = opts.ms_project %}
{% set data = cfg.data %}
{% set scfg = salt['mc_utils.json_dump'](cfg) %}

prepare-elevation-charts-{{cfg.name}}:
  cmd.run:
    - name: bin/django prepare_elevation_charts --url=http://{{ data.domain }}
    - cwd: {{cfg.project_root}}
    - user: {{cfg.user}}
