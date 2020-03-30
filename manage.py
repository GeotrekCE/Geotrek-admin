#!/usr/bin/env python3
import os
import pwd
import sys


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geotrek.settings")

    from django.core.management import execute_from_command_line

    if sys.argv[0].endswith('geotrek'):
        user = pwd.getpwnam('geotrek')
        os.setgid(user.pw_gid)
        os.setuid(user.pw_uid)

    execute_from_command_line(sys.argv)
