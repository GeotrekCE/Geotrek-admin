{% set cfg = opts.ms_project %}

geotrek-overlay:
    file.recurse:
        - name: {{cfg.project_root}}
        - source: salt://makina-projects/{{cfg.name}}/files/overlay
        - makedirs: true

geotrek-settings-ini:
    file.managed:
        - name: {{cfg.project_root}}/etc/settings.ini
        - source: salt://makina-projects/{{cfg.name}}/files/settings.ini
        - makedirs: true
        - template: jinja
        - defaults:
            data: {{cfg.data}}

geotrek-install:
    cmd.run:
        - name: {{cfg.project_root}}/install.sh --prod --noinput
        - cwd: {{cfg.project_root}}
        - env:
            - LC_ALL: fr_FR.UTF-8
