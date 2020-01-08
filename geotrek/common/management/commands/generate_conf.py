from os.path import join

from django.conf import settings
from django.core.management.base import BaseCommand
from django.template.loader import get_template


class Command(BaseCommand):
    help = "Generate configuration files"

    def add_arguments(self, parser):
        parser.add_argument('--user', default='root', help="User (default to root)")
        parser.add_argument('--standalone', action='store_true', help="Add conf for convertit and screamshotter")

    def handle(self, *args, **options):
        conf_settings = (
            'BASE_DIR', 'VAR_DIR', 'STATIC_ROOT', 'MEDIA_ROOT',
            'GUNICORN_CONF', 'CONVERTIT_CONF', 'SCREAMSHOTTER_CONF', 'NGINX_CONF'
        )
        context = {name: getattr(settings, name) for name in conf_settings}
        context['user'] = options['user']
        filenames = [
            'nginx.conf',
            'convertit.cfg',
            'logrotate.conf',
            'gunicorn-geotrek.conf.py',
            'gunicorn-geotrek_api.conf.py',
            'supervisor-geotrek.conf',
            'supervisor-geotrek-api.conf',
            'supervisor-geotrek-celery.conf',
        ]
        if options['standalone']:
            filenames.extend([
                'gunicorn-convertit.conf.py',
                'gunicorn-screamshotter.conf.py',
                'supervisor-convertit.conf',
                'supervisor-screamshotter.conf',
            ])
        for filename in filenames:
            template = get_template(join('conf', filename))
            content = template.render(context)
            with open(join(settings.VAR_DIR, 'conf', filename), 'w') as f:
                f.write(content)
