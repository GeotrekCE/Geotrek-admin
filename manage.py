#!/usr/bin/env python
import os
import sys

activate_script = os.path.join(os.path.dirname(__file__), 'bin/activate_this.py')
execfile(activate_script, {'__file__': activate_script})

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geotrek.settings.default")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
