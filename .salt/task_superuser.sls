{% set cfg = opts.ms_project %}
{% set data = cfg.data %}
{% set ds = data %}

{% macro set_env() %}
    - env:
      - DJANGO_SETTINGS_MODULE: "{{data.DJANGO_SETTINGS_MODULE}}"
{% endmacro %}

{% if data.get('create_admins', True) %}
{% for dadmins in data.admins %}
{% for admin, udata in dadmins.items() %}
{% set f = data.app_root + '/salt_' + admin + '_check.py' %}
user-{{cfg.name}}-{{admin}}:
  file.managed:
    - name: "{{f}}"
    - contents: |
                #!{{data.py}}
                import os
                try:
                    import django;django.setup()
                except Exception:
                    pass
                from {{ds.USER_MODULE}} import {{ds.USER_CLASS}} as User
                User.objects.filter(username='{{admin}}').all()[0]
                if os.path.isfile("{{f}}"):
                    os.unlink("{{f}}")
    - mode: 700
    - template: jinja
    - user: {{cfg.user}}
    - group: {{cfg.group}}
    - source: ""
    - cwd: {{data.app_root}}
    - user: {{cfg.user}}
  cmd.run:
    - name: {{data.create_user}} createsuperuser --username="{{admin}}" --email="{{udata.mail}}" --noinput
    - unless: "{{f}}"
    {{set_env()}}
    - cwd: {{data.app_root}}
    - user: {{cfg.user}}
    - watch:
      - file: "user-{{cfg.name}}-{{admin}}"

{% set f = data.app_root + '/salt_' + admin + '_password.py' %}
superuser-{{cfg.name}}-{{admin}}:
  file.managed:
    - contents: |
                #!{{data.py}}
                import os
                try:
                    import django;django.setup()
                except Exception:
                    pass
                from {{ds.USER_MODULE}} import {{ds.USER_CLASS}} as User
                user=User.objects.filter(username='{{admin}}').all()[0]
                user.set_password('{{udata.password}}')
                user.email = '{{udata.mail}}'
                user.save()
                if os.path.isfile("{{f}}"):
                    os.unlink("{{f}}")
    - template: jinja
    - mode: 700
    - user: {{cfg.user}}
    - group: {{cfg.group}}
    - name: "{{f}}"
  cmd.run:
    {{set_env()}}
    - name: {{f}}
    - cwd: {{data.app_root}}
    - user: {{cfg.user}}
    - watch:
      - cmd: "user-{{cfg.name}}-{{admin}}"
      - file: "superuser-{{cfg.name}}-{{admin}}"
{%endfor %}
{%endfor %}
{%endif %}

