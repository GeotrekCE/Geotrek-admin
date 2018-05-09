#!/usr/bin/env python
import os
import sys

try:
    activate_script = os.path.join(os.path.dirname(__file__), '../venv/bin/activate_this.py')
    execfile(activate_script, {'__file__': activate_script})
except IOError as exc:
    print('virtualenv is not available. (%s)' % exc)


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geotrek.settings.prod")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)