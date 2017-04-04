{% set cfg = opts.ms_project %}

include:
  - makina-states.services.http.nginx 

{{cfg.name}}-linknginx:
  file.symlink:
    - names:
      - /etc/nginx/conf.d/geotrek.conf
      - /etc/nginx/sites-enabled/geotrek
    - makedirs: true
    - target: /etc/nginx/sites-available/geotrek
    - watch_in:
      - mc_proxy: nginx-pre-hardrestart-hook
    - watch:
      - mc_proxy: nginx-post-conf-hook
