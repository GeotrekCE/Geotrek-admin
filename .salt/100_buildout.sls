{% set cfg = opts.ms_project %}
{% set data = cfg.data %}

include:
  - makina-projects.{{cfg.name}}.task_djangosettings

# duplicated settings to be sure of the extended value
# as settings are read first
{{cfg.name}}-buildout:
  file.managed:
    - name: {{cfg.project_root}}/salt.cfg
    - source: salt://makina-projects/{{cfg.name}}/files/salt.cfg
    - template: jinja
    - user: {{cfg.user}}
    - defaults:
        project: {{cfg.name}}
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
      - mc_proxy: {{cfg.name}}-configs-gen
  buildout.installed:
    - config: salt.cfg
    - name: {{cfg.project_root}}
    - user: {{cfg.user}}
    - use_vt: true
    - output_loglevel: info
    - watch:
      - file: {{cfg.name}}-buildout
    - user: {{cfg.user}}

