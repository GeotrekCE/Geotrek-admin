{% set cfg = opts.ms_project %}
{% set data = cfg.data %}
# ATTENTION you need to add a deploy key in https://github.com/makinacorpus/Geotrek-import/settings/keys
{{cfg.name}}-djangosettings:
  file.managed:
    - template: jinja
    - name: {{cfg.project_root}}/geotrek/settings/custom.py
    - source: {{data.django_settings_source}}
    - user: {{cfg.user}}
    - group: {{cfg.group}}
    - mode: 770
    - defaults:
        project: {{cfg.name}}
    - watch_in:
      - mc_proxy: {{cfg.name}}-configs-gen

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
    - watch_in:
      - mc_proxy: {{cfg.name}}-configs-gen
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

{{cfg.name}}-configs-gen:
  mc_proxy.hook: []
