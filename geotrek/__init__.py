import os
import pwd
import sys

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "VERSION")) as file_version:
    VERSION = file_version.read().strip()

__version__ = VERSION


def django_manage():
    """Use by geotrek command in debian based installations"""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geotrek.settings")

    from django.core.management import execute_from_command_line

    if sys.argv[0].endswith("geotrek"):
        if os.getuid() != 0:
            print("ERROR! This command should be run as root")
            sys.exit(1)
        user = pwd.getpwnam("geotrek")
        os.setgid(user.pw_gid)
        os.setuid(user.pw_uid)

    execute_from_command_line(sys.argv)
