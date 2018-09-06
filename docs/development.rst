.. _development-section:

===========
DEVELOPMENT
===========

This documentation is dedicated to code contributors, in order to run a development instance.

Developers are advice to run their *Geotrek* instance in an isolated environment,
however it is not an absolute prerequisite. More details below.


Isolated environment
--------------------

Deveopment stack is managed by docker and docker-compose

::

    make build

Why make build ? To run test and load data tests, geotrek user in docker container needs to have same UID that's your current user.
make build just pass your UID as argument to build development docker image.

Run
---

Start local instance :

::

    docker-compose up

.. note::

    Running ``docker-compose run web update.sh`` is recommended after a pull of new source code.


Run unit tests :

::

    docker-compose run web ./manage.py test --settings=geotrek.settings.tests


Run unit tests in verbose mode, and without migrations :

::

    docker-compose run web ./manage.py test --settings=geotrek.settings.tests -v 2


Development data
----------------

::

    docker-compose run web initial.sh

     docker-compose run web ./manage.py loaddata development-pne


In order to get elevation data, a DEM is necessary. If you use the default extent,
as defined in ``custom.py``, you can load the following dataset :

::

    wget http://depot.makina-corpus.org/public/geotrek/mnt_0_ecrins.zip -o geotrek/var/mnt_0_ecrins.zip
    unzip geotrek/var/mnt_0_ecrins.zip
     docker-compose run web ./manage.py loaddem /app/var/mnt_0_ecrins/w001001.adf


Conventions
-----------

* Use flake8
* KISS & DRY as much as possible
* Elegant and generic is good, simple is better
* Commits messages are explicit and mention issue number (``(ref #12)`` or ``(fixes #23)``)
* Features are developed in a branch and merged from Github pull-requests.


Definition of done
------------------

* ``docs/changelog.rst`` is up-to-date
* A unit-test covers the bugfix or the new feature
* A frontend test (:path:jstests/nav-*.js) covers the navigation bug fix or feature
* A JS *Mocha* test (:path:jstests/tests.*.js) covers the JavaScript bug fix or feature
* Unit-tests coverage is above or at least equal with previous commits
* Settings have default value in ``settings/base.py`` or ``conf/settings-default.ini``
* Installation instructions are up-to-date

Check TODO in the source tree ::

    find geotrek | xargs egrep -n -i '(TODO|XXX|temporary|FIXME)'


Release
-------

* Update *VERSION* file, *docs/conf.py*
* Pin (fixed revision) of eggs under development in *buildout.cfg*
* Use semantic versioning
* Use zest.releaser
* Add git tag X.Y.Z
* Add release on Github (copy-paste ``CHANGES`` paragraph)


Model modification
------------------

    docker-compose run web ./manage.py makemigrations <appName>
    docker-compose run web ./manage.py  migrate

:notes:

    Add migration file to source control.


Database reset
--------------

Data only:

::

    docker-compose run web ./manage.py  flush


Everything:

::

    dbname=geotrekdb
    sudo -n -u postgres -s -- psql -c "DROP DATABASE ${dbname};" && sudo -n -u postgres -s -- psql -c "CREATE DATABASE ${dbname};" && sudo -n -u postgres -s -- psql -d ${dbname} -c "CREATE EXTENSION postgis;"


Mapentity development
---------------------

To develop mapentity and Geotrek together, modify lines to ``requirement.txt``:

::

    [sources]
    mapentity = git https://github.com/makinacorpus/django-mapentity.git

    [buildout]
    auto-checkout += mapentity

Then run:

::

    make env_dev update
    cd lib/src/mapentity/
    git submodule init
    git submodule update
