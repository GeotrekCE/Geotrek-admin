{% set cfg = opts.ms_project %}
{% set data = cfg.data %}
{% set scfg = salt['mc_utils.json_dump'](cfg) %}
{% set sdata = salt['mc_utils.json_dump'](data) %}

# ATTENTION you need to add a deploy key in https://github.com/makinacorpus/Geotrek-import/settings/keys

{{cfg.name}}-djangosettings:
  file.managed:
    - template: jinja
    - name: {{cfg.project_root}}/geotrek/settings/custom.py
    - source: salt://makina-projects/{{cfg.name}}/files/config.py
    - user: {{cfg.user}}
    - group: {{cfg.group}}
    - mode: 770
    - defaults:
        data: |
              {{scfg}}

# duplicated settings to be sure of the extended value
# as settings are read first
{{cfg.name}}-settings:
  file.managed:
    - template: jinja
    - name: {{cfg.project_root}}/etc/settings.ini
    - source: salt://makina-projects/{{cfg.name}}/files/settings.cfg
    - user: {{cfg.user}}
    - group: {{cfg.group}}
    - mode: 770
    - watch:
      - file: {{cfg.name}}-djangosettings
    - defaults:
        data: |
              {{scfg}}
      {% if data.has_services %}
        configs: conf/buildout-prod-standalone.cfg
      {% else %}
        configs: conf/buildout-prod.cfg conf/tilecache.cfg
      {% endif %}
        parts: >
               ${buildout:base-parts}
               {% if data.has_guillestrois %}geotrek_import{%endif%}
               {% if data.has_geotrek %}${buildout:app-parts}{%endif%}
               {% if data.has_services %}${buildout:services-parts}{%endif%}
               ${buildout:maintenance-parts}

# duplicated settings to be sure of the extended value
# as settings are read first
{{cfg.name}}-buildout:
  file.managed:
    - name: {{cfg.project_root}}/salt.cfg
    - source: salt://makina-projects/{{cfg.name}}/files/salt.cfg
    - template: jinja
    - user: {{cfg.user}}
    - defaults:
        data: |
              {{scfg}}
      {% if data.has_services %}
        configs: conf/buildout-prod-standalone.cfg
      {% else %}
        configs: conf/buildout-prod.cfg conf/tilecache.cfg
      {% endif %}
        parts: >
               ${buildout:base-parts}
               {% if data.has_guillestrois %}geotrek_import{%endif%}
               {% if data.has_geotrek %}${buildout:app-parts}{%endif%}
               {% if data.has_services %}${buildout:services-parts}{%endif%}
               ${buildout:maintenance-parts}
    - group: {{cfg.group}}
    - makedirs: true
    - watch:
      - file: {{cfg.name}}-settings
  buildout.installed:
    - config: salt.cfg
    - name: {{cfg.project_root}}
    - user: {{cfg.user}}
    - use_vt: true
    - output_loglevel: info
    - watch:
      - file: {{cfg.name}}-buildout
    - user: {{cfg.user}}
    - group: {{cfg.group}}

