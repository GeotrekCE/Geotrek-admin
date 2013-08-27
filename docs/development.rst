===========
DEVELOPMENT
===========

For code contributors only : in order to run a development instance :

::

    ./install.sh --dev

Start local instance :

::

    make serve


Run unit tests :

::

    make tests

For PDF conversion server, run an instance of Convertit in a separate terminal on ``http://localhost:6543``

::

    bin/pserve lib/src/convertit/development.ini



Release
-------

* Update *VERSION* file, *docs/conf.py*
* Pin (fixed revision) of eggs under development in *buildout.cfg*
* Use semantic versioning
* Use zest.releaser
* Add git tag vx.x.x
* Add release on Github
