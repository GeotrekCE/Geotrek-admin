{% set cfg = opts.ms_project %}
{% set data = cfg.data %}
{% set scfg = salt['mc_utils.json_dump'](cfg) %}

prepare-map-image-{{cfg.name}}:
  cmd.run:
    - name: bin/django prepare_map_images --url=http://{{ salt['network.ip_addrs']('eth0')[0] }}
    - cwd: {{cfg.project_root}}
    - user: {{cfg.user}}
