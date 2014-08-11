{% set cfg = opts.ms_project %}
{% set data = cfg.data %}
{% set scfg = salt['mc_utils.json_dump'](cfg) %}
{% set sdata = salt['mc_utils.json_dump'](data) %}
{% set gtrois = data.gtrois %}
{% if data.has_guillestrois %}

{{cfg.name}}-create-dir:
  file.directory:
    - name: {{data.gtrois.xml_path}}
    - user: {{cfg.user}}
    - group: {{cfg.user}}
    - mode: 750
    - makedirs: true

{{cfg.name}}-create-table-gtrois:
  cmd.run:
    - name: psql -f lib/src/geotrek_import/import_data.sql -H "{{data.psql_url}}"
    - cwd: {{cfg.project_root}}
    - unless: echo "select * from import_data limit 1;"|psql  -v ON_ERROR_STOP=1 -H "{{data.psql_url}}" 1>2 2>/dev/null
    - watch:
      - file: {{cfg.name}}-create-dir

{{cfg.name}}-gtrois:
  file.managed:
    - watch:
      - cmd: {{cfg.name}}-create-table-gtrois
    - name: {{cfg.project_root}}/lib/src/geotrek_import/src/geotrek_import/Guillestrois/settings.py
    - source: salt://makina-projects/{{cfg.name}}/files/gtrois.py
    - template: jinja
    - user: {{cfg.user}}
    - defaults:
        data: |
              {{scfg}}
    - group: {{cfg.group}}
    - makedirs: true

{{cfg.name}}-cron-gtrois:
  file.managed:
    - watch:
      - file: {{cfg.name}}-gtrois
    - name: {{cfg.data_root}}/gtrois.sh
    - mode: 755
    - user: root
    - source: ''
    - contents: |
                #!/usr/bin/env bash
                LOG="{{cfg.data_root}}/gtrois.log"
                lock="${0}.lock"
                if [ -e "${lock}" ];then
                  echo "Locked ${0}";exit 1
                fi
                touch "${lock}"
                salt-call --out-file="${LOG}" --retcode-passthrough -lall\
                  --local mc_project.run_task {{cfg.name}} task_gtrois\
                  1>/dev/null 2>/dev/null
                ret="${?}"
                rm -f "${lock}"
                if [ "x${ret}" != "x0" ];then
                  cat "${LOG}"
                fi
                exit "${ret}"

{{cfg.name}}-run-cron-gtrois:
  file.managed:
    - watch:
      - file: {{cfg.name}}-cron-gtrois
    - name: /etc/cron.d/gtrois
    - mode: 700
    - user: root
    - source: ''
    - contents: |
                #!/usr/bin/env bash
                MAILTO="{{gtrois.mail}}"
                {{gtrois.periodicity}} root {{cfg.data_root}}/gtrois.sh
{% endif %}
