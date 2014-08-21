{% set cfg = opts.ms_project %}
{% set data = cfg.data %}
{% set scfg = salt['mc_utils.json_dump'](cfg) %}
{% set sdata = salt['mc_utils.json_dump'](data) %}

#
# {{cfg.name}}-logo-login:
#   file.managed:
#     - name: {{cfg.data_root}}/var/media/upload/logo-login.png
#     - source: {{data.path_logo_login}}
#     - user: {{cfg.user}}
#     - group: {{cfg.group}}
#     - makedirs: true
#
# {{cfg.name}}-logo-header:
#   file.managed:
#     - name: {{cfg.data_root}}/var/media/upload/logo-header.png
#     - source: {{data.path_logo_header}}
#     - user: {{cfg.user}}
#     - group: {{cfg.group}}
#     - makedirs: true
#
# {{cfg.name}}-favicon:
#   file.managed:
#     - name: {{cfg.data_root}}/var/media/upload/favicon.png
#     - source: {{data.path_favicon}}
#     - user: {{cfg.user}}
#     - group: {{cfg.group}}
#     - makedirs: true
#
# {{cfg.name}}-trek-public-template:
#   file.managed:
#     - name: {{cfg.data_root}}/var/media/templates/trekking/trek_public.odt
#     - source: {{data.path_trek_public_template}}
#     - user: {{cfg.user}}
#     - group: {{cfg.group}}
#     - makedirs: true
