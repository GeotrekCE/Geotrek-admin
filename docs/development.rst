.. _development-section:

===========
DEVELOPMENT
===========

This documentation is dedicated to code contributors, in order to run a development instance.

Developers are advice to run their *Geotrek* instance in an isolated environment,
however it is not an absolute prerequisite. More details below.


Isolated environment
--------------------

If you use virtual machines or containers (*Vagrant*, *LXC*, ...), this
will install all the necessary components for development :

::

    ./install.sh --dev


Directly on your host
---------------------

The most minimal components required to run an instance are :

* PostGIS 2 server
* GDAL, GEOS, libproj
* gettext
* libfreetype
* libxml2, libxslt
* Usual Python dev stuff

See `the list of minimal packages on Debian/Ubuntu <https://github.com/makinacorpus/Geotrek/blob/211cd/install.sh#L136-L148>`_.

If you already have all these components installed your OS (probably
because you're already a python/GIS developer), then just jump to the
next section !


Run
---

Start local instance :

::

    make env_dev update serve

.. note::

    Running ``env_dev`` and ``update`` is recommended after a pull of new source code,
    but is not mandatory : ``make serve`` is enough most of the time.


Run unit tests :

::

    make env_test update tests


Run unit tests in verbose mode, and without migrations :

::

    make env_dev update tests


For Capture server, run an instance of screamshotter in a separate terminal :

::

    bin/django runserver --settings=screamshotter.settings 8001


For PDF conversion server, run an instance of Convertit in a separate terminal on ``http://localhost:6543``

::

    bin/convertit lib/src/convertit/development.ini


Development data
----------------

::

    make load_data

    bin/django loaddata development-pne


In order to get elevation data, a DEM is necessary. If you use the default extent,
as defined in ``conf/settings.ini.sample``, you can load the following dataset :

::

    wget http://depot.makina-corpus.org/public/geotrek/mnt_0_ecrins.zip
    unzip mnt_0_ecrins.zip
    bin/django loaddem mnt_0_ecrins/w001001.adf


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

    bin/django makemigrations <appName>
    bin/django migrate

:notes:

    Add migration file to source control.


Database reset
--------------

Data only:

::

    bin/django flush


Everything:

::

    dbname=geotrekdb
    sudo -n -u postgres -s -- psql -c "DROP DATABASE ${dbname};" && sudo -n -u postgres -s -- psql -c "CREATE DATABASE ${dbname};" && sudo -n -u postgres -s -- psql -d ${dbname} -c "CREATE EXTENSION postgis;"


Mapentity development
---------------------

To develop mapentity and Geotrek together, add the following lines to ``etc/settings.ini``:

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
