#!/usr/bin/env bash
"exec" "`dirname $0`/env/bin/python" "$0" "$@"
import os
import sys


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geotrek.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
