{% set cfg = opts.ms_project %}
{% set data = cfg.data %}
{% set scfg = salt['mc_utils.json_dump'](cfg) %}
{% set sdata = salt['mc_utils.json_dump'](data) %}
{% if data.has_services and not data.has_geotrek %}
{{cfg.name}}-global-up:
  cmd.run:
    - name: bin/develop up -f
    - cwd: {{cfg.project_root}}
    - user: {{cfg.user}}
    - use_vt: true
    - output_loglevel: info
{% endif %}

{% if data.has_geotrek %}
{{cfg.name}}-geotrek-global-up:
  cmd.run:
    - name: make update
    - cwd: {{cfg.project_root}}
    - user: {{cfg.user}}
    - use_vt: true
    - output_loglevel: info
{% endif %}
