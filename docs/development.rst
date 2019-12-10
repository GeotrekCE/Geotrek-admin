.. _development-section:

===========
DEVELOPMENT
===========

Quickstart
----------

::

    cp .env-dev.dist .env
    cp docker-compose-dev.yml docker-compose.yml
    docker-compose run --rm web update.sh
    docker-compose run --rm web load_data.sh
    docker-compose run --rm web ./manage.py createsuperuser
    docker-compose up -d

Got to http://localhost:8001


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
    docker-compose run web ./manage.py migrate

:notes:

    Add migration file to source control.


Database reset
--------------

Data only:

::

    docker-compose run web ./manage.py  flush


Mapentity development
---------------------

TODO
