{% set cfg = opts.ms_project %}
{% set data = cfg.data %}
{% set scfg = salt['mc_utils.json_dump'](cfg) %}
{% set sdata = salt['mc_utils.json_dump'](data) %}
{% if data.has_guillestrois %}
{{cfg.name}}-cron-gtrois:
  file.managed:
    - name: {{cfg.project_root}}/bin/gtrois_geotrek_import.sh
    - cwd: {{cfg.project_root}}
    - contents: |
                #!/usr/bin/env bash
                export DJANGO_SETTINGS_MODULE="{{data.django_settings_module}}"
                $(dirname $0)/geotrek_import "${@}"
    - user: {{cfg.user}}
    - group: {{cfg.group}}
    - mode: 755
  cmd.run:
    - name: {{cfg.project_root}}/bin/gtrois_geotrek_import.sh
    - cwd: {{cfg.project_root}}
    - use_vt: true
    - output_loglevel: info
    - use_vt: true
    - output_loglevel: info
    - user: {{cfg.user}}
    - watch:
      - file: {{cfg.name}}-cron-gtrois
{% endif %}
