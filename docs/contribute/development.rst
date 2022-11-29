.. _development-section:

===========
Development
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

Go to http://localhost:8000

PDF generation might not work unless you add the following entry to ``/etc/hosts`` and use ``geotrek.local:8000`` to access Geotrek.

::

    127.0.0.1   localhost geotrek.local


Contribution guide
==================

Conventions
-----------

* Use flake8
* KISS & DRY as much as possible
* Elegant and generic is good, simple is better
* Commits messages are explicit and mention issue number (``(ref #12)`` or ``(fixes #23)``)
* Features are developed in a branch and merged from Github pull-requests. A git hook to is available to prevent pushing to master, to enable it, developpers should run the following command from root directory (`Geotrek-admin/`) : `ln -s -f ../../.githooks/pre-push .git/hooks/pre-push`


Definition of done
------------------

* ``docs/changelog.rst`` is up-to-date
* A unit-test covers the bugfix or the new feature
* A frontend test (:path:jstests/nav-\*.js) covers the navigation bug fix or feature
* A JS *Mocha* test (:path:jstests/tests.\*.js) covers the JavaScript bug fix or feature
* Unit-tests coverage is above or at least equal with previous commits
* Settings have default value in ``settings/base.py`` or ``conf/settings-default.ini``
* Installation instructions are up-to-date

Check TODO in the source tree:

::

   find geotrek | xargs egrep -n -i '(TODO|XXX|temporary|FIXME)'


Release
-------

On master branch:

* If need be, merge ``translations`` branch managed with https://weblate.makina-corpus.net
* Update files *VERSION*, *docs/conf.py* and *docs/changelog.rst* to remove ``+dev`` suffix and increment version (please use semver rules)
* Run ``dch -r -D RELEASED``, update version in the same way and save
* Commit with message 'Release x.y.z' to merge in ``master`` branch before release
* Add git tag X.Y.Z
* Update files *VERSION*, *docs/conf.py* and *docs/changelog.rst* to add ``+dev`` suffix
* Run ``dch -v <version>+dev --no-force-save-on-release`` and save
* Commit with message 'Back to development'
* Push branch and tag
* Add release on Github (copy-paste ``doc/changelog.rst`` paragraph)
* When creating a new release 'x.y.z' on github, Github actions will generate the .deb package file, and publish it on https://packages.geotrek.fr (see ``.circleci/config.yml`` file for details)


Developement
============

Model modification
------------------

::

   docker-compose run web ./manage.py makemigrations <appName>
   docker-compose run web ./manage.py migrate

.. note ::

    Add migration file to source control.

Model modification - Definition of Done for new model fields
------------------------------------------------------------

When updating or adding a new field ``my_field`` to a model ``MyModel``, please proceed with the following changes to ensure this field is included in existing functionalities.

**In** ``MyModel`` **class** :

- If ``my_field`` is a ``ForeignKey``, make sure to override ``related_name`` with an explicit set name

- Make sure to set ``verbose_name`` on the field and add proper translations in ``.po`` files

**Outside of model class** :

- To display ``my_field`` in detail views, add a row in template ``mymodel_detail_attributes.html``

- Look for form class ``MyModelForm(CommonForm)`` :

    - If it exists, and field needs to be included in form, add ``my_field`` to form attributes (``fields`` on the ``Meta`` class, sometimes ``fieldslayout`` as well).

    - If field is added to the form **and is optional**, please add ``my_field`` to the documentation for hideable form fields : in ``docs/advanced-configuration.rst`` look for ``HIDDEN_FORM_FIELDS['mymodel']`` and add your field to the list.

- Look for list view class ``MyModelList(CustomColumnsMixin, MapEntityList)`` :

    - If it exists, please add ``my_field`` to the documentation for custom list view columns : in ``docs/advanced-configuration.rst`` look for ``COLUMNS_LISTS['mymodel_view']`` and add your field to the list.

    - If it exists, and if you wish to display a column for ``my_field`` in the list view for this model by default, simply add ``my_field`` to ``default_extra_colums`` on this class.

- Look for exports view class ``MyModelFormatList(MapEntityFormat, MyModelList)`` :

    - If it exists, please add ``my_field`` to the documentation for custom list exports columns : in ``docs/advanced-configuration.rst`` look for ``COLUMNS_LISTS['mymodel_export']`` and add your field to the list.

    - If it exists, and if you wish to display a column for ``my_field`` in CSV/SHP exports for this model by default, simply add ``my_field`` to ``default_extra_colums`` on this class.

- Follow the documentation you just edited to test that custom columns and hideable fields do work properly with your new field.

- Look for sql file defaults ``geotrek/{app_name}/sql/post_90_defaults.sql`` :

    - If it exists find your modelname in the list and depending on the default value alter column ``my_field`` or add ``-- my_field``

    - If the modelname doesn't exist, create a new section (even if you don't need to alter column)

- Look for sql view file ``geotrek/{app_name}/sql/post_20_views.sql`` and update the view for your model with an alias for the new field


**In API v2** :

If ``MyModel`` is served by APIv2, make sure to add a serializer for the new field in ``geotrek/api/v2/serializers.py`` and if you wish to filter on this field, create a new filter and add it to the right ``ViewSet`` under ``geotrek/api/v2/views``, using attribute ``filter_backends``.


When updating a field ``my_field`` in a model ``MyModel`` for ``new_field``, check if this field is translated in ``geotrek/{app}/translation.py``.

If so, you need to add a migration just after the migration generated by django.
This migration should rename the old fields generated by modeltranslation ``my_field_en`` by ``new_field_en``
(example : ``geotrek/trekking/migrations/0014_auto_20200228_2127.py``)


Run tests
---------

**Django tests :**

``ENV`` variable must be set to run tests:

::

   docker-compose run --rm -e ENV=tests web ./manage.py test

Test without dynamic segmentation:

::

   docker-compose run --rm -e ENV=tests_nds web ./manage.py test


**Cypress tests :**

Create an empty project with docker :

::

    docker-compose down
    docker-compose up -d


Install elements for the cypress tests

::

    make load_data
    make load_test_integration
    make load_test_integration_workflow


Move in cypress folder and install

::

    cd cypress
    npm ci


Launch tests

::

    ./node_modules/.bin/cypress run


Pictures of the problem and videos are generated in cypress/videos and cypress/screenshots

Setup to run rando synchronization locally
------------------------------------------

(sync rando is only relevant for an admin paired with geotrek rando v2)

In your django settings you must set the 'url' key of SYNC_RANDO_OPTIONS to use the same domain as defined by SERVER_NAME in your .env.

For instance with SERVER_NAME=geotrek.local (default value)

::

	SYNC_RANDO_OPTIONS = {
		'url': 'http://geotrek.local:8000'
	}

Setup to use screamshotter-related features locally
---------------------------------------------------

Use the domain defined in SERVER_NAME in your .env to reach your local geotrek admin web instance. By default the address is `http://geotrek.local:8000`.

Update the `/etc/hosts` on your machine to resolve `geotrek.local` on `127.0.0.1`.

::

	$ cat /etc/hosts
	127.0.0.1	geotrek.local
	127.0.0.1	localhost

Database reset
--------------

Data only:

::

   docker-compose run web ./manage.py flush

Restore existing Database
-------------------------

Assuming a dump of your database is located in your project directory:

::

   docker-compose run --rm web pg_restore --clean --no-owner --no-acl -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB /opt/geotrek-admin/<path_to_backup>.dump

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

Documentation
=============

A container based on sphinx image is created using docker-compose-dev.yml,
documentation is built in watch mode thanks to sphinx-autobuild.

Access to documentation built in html : http://0.0.0.0:8800


Translate documentation
-----------------------

- Generate .pot if needed

.. code-block :: python

    docker-compose run --rm sphinx make gettext

- Generate .po files

.. code-block :: python

    docker-compose run --rm sphinx sphinx-intl update -p _build/locale -l fr
