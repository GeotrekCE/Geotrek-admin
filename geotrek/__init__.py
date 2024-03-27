import os
import subprocess
import toml

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(os.path.dirname(here), "pyproject.toml")) as file_version:
    toml_content = toml.loads(file_version.read())
    __version__ = toml_content["project"]["version"]


def cmd():
    cmd = [
        "python",
        "../manage.py",
    ]
    subprocess.run(cmd)
