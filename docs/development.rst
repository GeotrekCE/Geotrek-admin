===========
DEVELOPMENT
===========

For code contributors only : in order to run a development instance :

::

    ./install.sh --dev

Start local instance :

::

    make env_dev serve


Run unit tests :

::

    make env_test tests


Run unit tests (verbose mode, and without migrations) :

::

    make env_dev tests


For Capture server, run an instance of screamshotter in a separate terminal :

::

    bin/django runserver --settings=screamshotter.settings 8001


For PDF conversion server, run an instance of Convertit in a separate terminal on ``http://localhost:6543``

::

    bin/pserve lib/src/convertit/development.ini


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
* Commits messages are explicit and mention issue number (``(ref #12)``)
* Huge refactors or features are developed in a branch and merged with as Github pull-request.
* KISS & DRY as much as possible
* Elegant and generic is good, simple is better


Definition of done
------------------

* ``CHANGES`` is up-to-date
* Unit-tests coverage is above or at least equal with previous commits
* Settings have default value in ``settings/base.py`` or ``conf/settings-default.ini``
* Installation instructions are up-to-date

Check TODO in the source tree ::

    find caminae | xargs egrep -n -i '(TODO|temporary|FIXME)'


Release
-------

* Update *VERSION* file, *docs/conf.py*
* Pin (fixed revision) of eggs under development in *buildout.cfg*
* Use semantic versioning
* Use zest.releaser
* Add git tag vx.x.x
* Add release on Github (copy-paste ``CHANGES`` paragraph)

Bug-fix releases :

* Create branch with main version (e.g. ``0.20``)


Model modification
------------------

    bin/django schemamigration <appName> --auto
    bin/django syncdb --migrate

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

