
{% set cfg = opts['ms_project'] %}
{# export macro to callees #}
{% set locs = salt['mc_locations.settings']() %}
{% set cfg = opts['ms_project'] %}
{{cfg.name}}-restricted-perms:
  file.managed:
    - name: {{cfg.project_dir}}/global-reset-perms.sh
    - mode: 755
    - user: root
    - group: root
    - contents: |
            #!/usr/bin/env bash
            # hack to be sure that nginx is in www-data
            # in most cases
            datagroup="{{cfg.group}}"
            groupadd -r $datagroup || /bin/true
            gpasswd -a nginx $datagroup || /bin/true
            gpasswd -a www-data $datagroup || /bin/true
            # be sure to remove POSIX acls support
            setfacl -P -R -b -k "{{cfg.project_dir}}"
            "{{locs.resetperms}}" -q --no-acls\
              --user root --group "{{cfg.group}}" \
              --dmode '0770' --fmode '0770' \
              --paths "{{cfg.pillar_root}}";
            find -H \
              "{{cfg.project_root}}" \
              "{{cfg.data_root}}" \
              -type f -or -type d -not -path "{{cfg.data_root}}/var/media/paperclip" | while read i;do
                if [ ! -h "${i}" ];then
                  if [ -d "${i}" ];then
                    chmod g-s "${i}"
                    chown {{cfg.user}}:$datagroup "${i}"
                    chmod g+s "${i}"
                  elif [ -f "${i}" ];then
                    chown {{cfg.user}}:$datagroup "${i}"
                  fi
                fi
            done
            "{{locs.resetperms}}" -q --no-acls --no-recursive\
              --user root --group root --dmode '0551' --fmode '0555' \
              --paths "{{cfg.project_dir}}/global-reset-perms.sh" \
              --paths "{{cfg.project_root}}"/.. \
              --paths "{{cfg.project_root}}"/../..;
  cmd.run:
    - name: {{cfg.project_dir}}/global-reset-perms.sh
    - cwd: {{cfg.project_root}}
    - user: root
    - watch:
      - file: {{cfg.name}}-restricted-perms

