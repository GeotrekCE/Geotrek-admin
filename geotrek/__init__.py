import os

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "VERSION")) as file_version:
    __version__ = file_version.read().strip()
