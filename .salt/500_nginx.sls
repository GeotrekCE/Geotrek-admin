{% set cfg = opts.ms_project %}
{% set data = cfg.data %}
{% if not data.has_geotrek %}
noop: {mc_proxy.hook: []}
{%else%}
include:
  - makina-states.services.http.nginx

etc-nginxa-supervisor.{{cfg.name}}:
  file.symlink:
    - name: /etc/nginx/sites-available/{{cfg.name}}.conf
    - target: {{cfg.project_root}}/etc/nginx.conf

etc-nginxe-supervisor.{{cfg.name}}:
  file.symlink:
    - name: /etc/nginx/sites-enabled/{{cfg.name}}.conf
    - target: /etc/nginx/sites-available/{{cfg.name}}.conf
    - watch:
      - file: etc-nginxa-supervisor.{{cfg.name}}
    - watch_in:
      - cmd: {{cfg.name}}-nginx-dummy

{{cfg.name}}-nginx-dummy:
  cmd.run:
    - name: echo
    - watch_in:
      - mc_proxy: nginx-post-conf-hook

{# atm tilecache cant auth
{% if cfg.default_env in ['staging'] %}
{{cfg.name}}-htaccess-conf:
  file.managed:
    - name: {{cfg.project_root}}/etc/nginx.d/htaccess.conf
    - source: ''
    - contents: |
                auth_basic "Restricted";
                auth_basic_user_file  {{data.htaccess}};
    - user: www-data
    - group: www-data
    - mode: 770
{{cfg.name}}-htaccess:
  file.managed:
    - watch:
       - file: {{cfg.name}}-htaccess-conf
    - name: {{data.htaccess}}
    - source: ''
    - user: www-data
    - group: www-data
    - mode: 770

{% for userdata in data.users %}
{% for user, passwd in userdata.items() %}
{{cfg.name}}-{{user}}-htaccess:
  webutil.user_exists:
    - name: {{user}}
    - password: {{passwd}}
    - htpasswd_file: {{data.htaccess}}
    - options: m
    - force: true
    - watch:
      - file: {{cfg.name}}-htaccess
    - watch_in:
      - mc_proxy: nginx-pre-conf-hook
{% endfor%}
{% endfor%}
{%else %}
{% endif %}
#}

{{cfg.name}}-htaccess-conf:
  file.absent:
    - name: {{cfg.project_root}}/etc/nginx.d/htaccess.conf
    - watch_in:
      - mc_proxy: nginx-pre-conf-hook
{% endif %}
