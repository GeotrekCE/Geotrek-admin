#!/usr/bin/env python
import os
import sys

exec(open("./bin/activate_this.py").read())
if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geotrek.settings.default")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)