{% set cfg = opts.ms_project %}
{% set data = cfg.data %}
{% set scfg = salt['mc_utils.json_dump'](cfg) %}

include:
  - makina-states.services.gis.ubuntugis
{% if data.has_services %}
  - makina-states.localsettings.phantomjs
  - makina-states.localsettings.casperjs
{% endif %}

{{cfg.name}}-www-data:
  user.present:
    - name: www-data
    - optional_groups:
      - {{cfg.group}}
    - remove_groups: false

prepreqs-{{cfg.name}}:
  pkg.installed:
    - watch:
      - mc_proxy: ubuntugis-post-conf-hook
      - user: {{cfg.name}}-www-data
    - pkgs:
      - sqlite3
      - libsqlite3-dev
      - apache2-utils
      - autoconf
      - automake
      - build-essential
      - bzip2
      - gettext
      - git
      - groff
      - libbz2-dev
      - libcurl4-openssl-dev
      - libdb-dev
      - libgdbm-dev
      - libreadline-dev
      - libfreetype6-dev
      - libsigc++-2.0-dev
      - libsqlite0-dev
      - libsqlite3-dev
      - libtiff5
      - libtiff5-dev
      - libwebp5
      - libwebp-dev
      - libssl-dev
      - libtool
      - libxml2-dev
      - libxslt1-dev
      - libopenjpeg-dev
      - libopenjpeg2
      - m4
      - man-db
      - pkg-config
      - poppler-utils
      - python-dev
      - python-imaging
      - python-setuptools
      - tcl8.4
      - tcl8.4-dev
      - tcl8.5
      - tcl8.5-dev
      - tk8.5-dev
      - wv
      {% if data.has_services %}
      - zlib1g-dev
      - libreoffice
      - unoconv
      - inkscape
      {% endif %}
      #
      - libjson0
      - libproj0
      - libgeos-c1
      - gdal-bin
      - libgdal-dev
      #
      - postgresql-client-9.3
      - postgresql-server-dev-all
      - memcached

{{cfg.name}}-dirs:
  file.directory:
    - makedirs: true
    - user: {{cfg.user}}
    - group: {{cfg.group}}
    - watch:
      - pkg: prepreqs-{{cfg.name}}
    - names:
      - {{cfg.data_root}}/lib
      - {{cfg.data_root}}/lib/parts
      - {{cfg.data_root}}/lib/src
      - {{cfg.data_root}}/lib/eggs
      - {{cfg.data_root}}/lib/develop-eggs
      - {{cfg.data_root}}/etc
      - {{cfg.data_root}}/var
      - {{cfg.data_root}}/parts
      - {{cfg.data_root}}/cache

{% for i in ['etc', 'var', 'lib'] %}
{{cfg.name}}-dirs-lnk-{{i}}:
  file.symlink:
    - target: {{cfg.data_root}}/{{i}}
    - name: {{cfg.project_root}}/{{i}}
    - watch:
      - file: {{cfg.name}}-dirs
{% endfor%}
