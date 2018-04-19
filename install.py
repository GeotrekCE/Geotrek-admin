import invoke
import sys

invoke.run("sudo apt-get install libgeos-c1v5 libproj9")
invoke.run("sudo apt-get install -y -q --no-upgrade libjson0 gdal-bin libgdal-dev libssl-dev binutils libproj-dev")
invoke.run("sudo apt-get install -y -qq language-pack-en-base language-pack-fr-base", hide=True, warn=True)
invoke.run("sudo locale-gen fr_FR.UTF-8",hide=True, warn=True)


if sys.argv[1] == "true":
    invoke.run("bin/pip install -r requirements.txt", hide=True, warn=True)
    invoke.run("bin/pip install -r requirements_dev.txt", hide=True, warn=True)
elif sys.argv[2] == "true":
    invoke.run("bin/pip install -r requirements.txt", hide=True, warn=True)
    invoke.run("bin/pip install -r requirements_tests.txt", hide=True, warn=True)
else:
    invoke.run("bin/pip install -r requirements.txt", warn=True)

invoke.run("bin/pip install --no-deps -r editable.txt", warn=True)