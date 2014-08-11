{% set cfg = opts.ms_project %}
{% set data = cfg.data %}
{%- set locations = salt['mc_locations.settings']() %}
# ensure at the bootstrap stage that user has permission execution on supervisor binaries
{{cfg.name}}-restricted-perms:
  file.managed:
    - name: {{cfg.project_dir}}/binaries-perms.sh
    - mode: 750
    - user: {% if not cfg.no_user%}{{cfg.user}}{% else -%}root{% endif %}
    - group: {{cfg.group}}
    - contents: |
            if [ -e "{{cfg.project_root}}" ];then
              "{{locations.resetperms}}" "${@}" \
              --dmode '0770' --fmode '0770'  \
              --paths "{{cfg.project_root}}"/bin \
              --users www-data \
              --users {% if not cfg.no_user%}{{cfg.user}}{% else -%}root{% endif %} \
              --groups {{cfg.group}} \
              --user {% if not cfg.no_user%}{{cfg.user}}{% else -%}root{% endif %} \
              --group {{cfg.group}};
            fi
  cmd.run:
    - name: {{cfg.project_dir}}/binaries-perms.sh
    - cwd: {{cfg.project_root}}
    - user: root
    - watch:
      - file: {{cfg.name}}-restricted-perms
{#- copy upstart job (no link, upstart is not always fine
    with symlinks#}
etc-init-supervisor.{{cfg.name}}:
  cmd.run:
    - name: >
            cp -fv
            {{cfg.project_root}}/etc/init/supervisor.conf
            /etc/init/supervisor_{{cfg.name}}.conf && echo "changed='false'"
    - stateful: true
    - watch:
      - cmd: {{cfg.name}}-restricted-perms

{{cfg.name}}-service:
  service.running:
    - name: supervisor_{{cfg.name}}
    - enable: True
    - watch:
      - cmd: etc-init-supervisor.{{cfg.name}}
  cmd.run:
    - name: service supervisor_{{cfg.name}} restart
    - onlyif: test "$({{cfg.project_root}}/bin/supervisorctl status 2>&1 |grep "refused connection"|wc -l)" != 0
    - user: root
    - watch:
      - service: {{cfg.name}}-service

{{cfg.name}}-reboot:
  file.managed:
    - name: {{cfg.data_root}}/restart.sh
    - user: root
    - group: root
    - mode: 755
    - contents: |
                #!/usr/bin/env bash
                {% if data.has_services %}
                {{cfg.project_root}}/bin/supervisorctl restart convertit
                {{cfg.project_root}}/bin/supervisorctl restart screamshotter
                {% endif %}
                {% if data.has_geotrek %}
                {{cfg.project_root}}/bin/supervisorctl restart geotrek
                {{cfg.project_root}}/bin/supervisorctl restart geotrek_api
                {{cfg.project_root}}/bin/supervisorctl restart tilecache
                {%- endif %}
  cmd.run:
    - name: {{cfg.data_root}}/restart.sh && service memcached restart
    - user: root
    - watch:
      - cmd: {{cfg.name}}-service

# attention files mode is picky for logrotate !
etc-logrotate.{{cfg.name}}:
  cmd.run:
    - name: |
            cp {{cfg.project_root}}/etc/logrotate.conf /etc/logrotate.d/{{cfg.name}}
            chmod 644 "/etc/logrotate.d/{{cfg.name}}"
