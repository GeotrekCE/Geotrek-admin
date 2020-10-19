.. _development-section:

===========
DEVELOPMENT
===========

Quickstart
==========

::

    cp .env-dev.dist .env
    # Edit .env if need be
    cp docker-compose-dev.yml docker-compose.yml
    docker-compose build
    docker-compose run --rm web update.sh
    docker-compose run --rm web load_data.sh
    docker-compose run --rm web ./manage.py createsuperuser
    docker-compose up -d

Got to http://localhost:8000


Contribution guide
==================

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

Check TODO in the source tree:

::

   find geotrek | xargs egrep -n -i '(TODO|XXX|temporary|FIXME)'


Release
-------

On master branch:
* If need be, merge ``translations`` branch managed with https://weblate.makina-corpus.net,
* Update files *VERSION*, *docs/conf.py* and *docs/changelog.rst* to remove ``~dev0`` suffix
* Run ``dch -r -D bionic``, remove ``~dev0`` suffix in version and save
* Commit with message 'Release x.y.z'
to merge in ``master`` branch before release
* Add git tag X.Y.Z
* Update files *VERSION*, *docs/conf.py* and *docs/changelog.rst* to increment version (using semantic versionning) 
and add ``.dev0v suffix
* Run ``dch -v <future version>~dev0 --no-force-save-on-release`` and save
* Commit with message 'Back to development'
* Push branch and tag
* When pushing a release tag 'x.y.z', CircleCI will generate the .deb package file, 
and publish it on https://packages.geotrek.fr (see ``.circleci/config.yml`` file for details)
* Add release on Github (copy-paste ``doc/changelog.rst`` paragraph)


Developement
============

Model modification
------------------

::

   docker-compose run web ./manage.py makemigrations <appName>
   docker-compose run web ./manage.py migrate

.. note ::

    Add migration file to source control.


Run tests
---------

``ENV`` variable must be set to run tests:

::

   docker-compose run --rm -e ENV=tests web ./manage.py test

Test without dynamic segmentation:

::

   docker-compose run --rm -e ENV=tests_nds web ./manage.py test


Database reset
--------------

Data only:

::

   docker-compose run web ./manage.py flush

Restore existing Database
-------------------------

Assuming a dump of your database is located in your project directory:

::

   docker-compose run --rm web pg_restore -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB /opt/geotrek/<path_to_backup>.dump

Restore your ``./var/conf/`` project files, and data files into ``./var/media``.

Then run a synchronization.

Mapentity development
---------------------

TODO


UML diagrams of data model
--------------------------

UML diagrams of Geotrek-admin data models are available in ``docs/data-model`` directory.
To regenerate them from PostgreSQL, install postgresql-autodoc and graphviz Ubuntu packages
and run ``make uml``.