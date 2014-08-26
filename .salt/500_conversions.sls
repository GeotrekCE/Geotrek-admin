{% set cfg = opts.ms_project %}
{% set data = cfg.data %}

{% if data.prepare_map_images_periodicity %}
{{cfg.name}}-scron-prepare-map-images:
  file.managed:
    - name: {{cfg.data_root}}/prepare_map_images.sh
    - mode: 750
    - contents: |
                #!/usr/bin/env bash
                LOG="{{cfg.data_root}}/var/log/prepare_map_images.log"
                lock="${0}.lock"
                if [ -e "${lock}" ];then
                  echo "Locked ${0}";exit 1
                fi
                touch "${lock}"
                salt-call --out-file="${LOG}" --retcode-passthrough -lall --local mc_project.run_task {{cfg.name}} task_prepare_map_images 1>/dev/null 2>/dev/null
                ret="${?}"
                rm -f "${lock}"
                if [ "x${ret}" != "x0" ];then
                  cat "${LOG}"
                fi
                exit "${ret}"

{{cfg.name}}-cron-prepare-map-images:
  file.managed:
    - name: /etc/cron.d/geotrek_prepare_map_images
    - mode: 750
    - contents: |
                {{data.prepare_map_images_periodicity}} root {{cfg.data_root}}/prepare_map_images.sh
{% endif %}



{% if data.prepare_elevation_charts_periodicity %}
{{cfg.name}}-scron-prepare-elevation-charts:
  file.managed:
    - name: {{cfg.data_root}}/prepare_elevation_charts.sh
    - mode: 750
    - contents: |
                #!/usr/bin/env bash
                LOG="{{cfg.data_root}}/var/log/prepare_elevation_charts.log"
                lock="${0}.lock"
                if [ -e "${lock}" ];then
                  echo "Locked ${0}";exit 1
                fi
                touch "${lock}"
                salt-call --out-file="${LOG}" --retcode-passthrough -lall --local mc_project.run_task {{cfg.name}} task_prepare_elevation_charts 1>/dev/null 2>/dev/null
                ret="${?}"
                rm -f "${lock}"
                if [ "x${ret}" != "x0" ];then
                  cat "${LOG}"
                fi
                exit "${ret}"

{{cfg.name}}-cron-prepare-elevation-charts:
  file.managed:
    - name: /etc/cron.d/geotrek_prepare_elevation_charts
    - mode: 750
    - contents: |
                {{data.prepare_elevation_charts_periodicity}} root {{cfg.data_root}}/prepare_elevation_charts.sh
{% endif %}
