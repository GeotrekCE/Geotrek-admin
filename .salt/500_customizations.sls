{% set cfg = opts.ms_project %}
{% set data = cfg.data %}
{% set scfg = salt['mc_utils.json_dump'](cfg) %}
{% set sdata = salt['mc_utils.json_dump'](data) %}


{% if data.has_geotrek %}
#
# Application logo customizations
#
{{cfg.name}}-logo-login:
  file.managed:
    - name: {{cfg.data_root}}/var/media/upload/logo-login.png
    - source: {{data.path_logo_login}}
    - user: {{cfg.user}}
    - group: {{cfg.group}}
    - makedirs: true

{{cfg.name}}-logo-header:
  file.managed:
    - name: {{cfg.data_root}}/var/media/upload/logo-header.png
    - source: {{data.path_logo_header}}
    - user: {{cfg.user}}
    - group: {{cfg.group}}
    - makedirs: true

{{cfg.name}}-favicon:
  file.managed:
    - name: {{cfg.data_root}}/var/media/upload/favicon.png
    - source: {{data.path_favicon}}
    - user: {{cfg.user}}
    - group: {{cfg.group}}
    - makedirs: true

{% if data.path_trek_public_template %}
{{cfg.name}}-trek-public-template:
  file.managed:
    - name: {{cfg.data_root}}/var/media/templates/trekking/trek_public.odt
    - source: {{data.path_trek_public_template}}
    - user: {{cfg.user}}
    - group: {{cfg.group}}
    - makedirs: true
{% endif %}

{% if data.path_touristiccontent_public_template %}
{{cfg.name}}-touristiccontent-public-template:
  file.managed:
    - name: {{cfg.data_root}}/var/media/templates/tourism/touristiccontent_public.odt
    - source: {{data.path_touristiccontent_public_template}}
    - user: {{cfg.user}}
    - group: {{cfg.group}}
    - makedirs: true
{% endif %}

{% if data.path_touristicevent_public_template %}
{{cfg.name}}-touristicevent-public-template:
  file.managed:
    - name: {{cfg.data_root}}/var/media/templates/tourism/touristicevent_public.odt
    - source: {{data.path_touristicevent_public_template}}
    - user: {{cfg.user}}
    - group: {{cfg.group}}
    - makedirs: true
{% endif %}

{% if data.path_locale %}
{{cfg.name}}-locale:
  file.recurse:
    - name: {{cfg.project_dir}}/project/geotrek/locale
    - source: {{data.path_locale}}
    - user: {{cfg.user}}
    - group: {{cfg.group}}
    - makedirs: true
{% endif %}
{% endif %}


{% if data.has_services %}
#
# Custom fonts are necessary for PDF conversions
#
{% for font in data.custom_fonts %}
{{cfg.name}}-custom-fonts-{{loop.index}}:
  file.managed:
    - name: /usr/local/share/fonts/{{font}}
    - source: "salt://makina-projects/{{cfg.name}}/files/{{font}}"
    - makedirs: true
{% endfor %}

{{cfg.name}}-refresh-font-cache:
  cmd.run:
    - name: /usr/bin/fc-cache
    - watch:
      - file: {{cfg.name}}-custom-fonts-1
{% endif %}