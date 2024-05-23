**Geotrek**, *paths* management for *National Parks* and *Tourism organizations*.

.. image:: http://geotrek.fr/assets/img/logo.svg

:master: |master-status| |master-coverage| |master-e2e| |master-rtd|

.. |master-status| image::
    https://github.com/GeotrekCE/Geotrek-admin/actions/workflows/test.yml/badge.svg
    :alt: CI Status
    :target: https://github.com/GeotrekCE/Geotrek-admin/actions/workflows/test.yml

.. |master-coverage| image::
    https://codecov.io/gh/GeotrekCE/Geotrek-admin/branch/master/graph/badge.svg
    :alt: Coverage
    :target: https://codecov.io/gh/GeotrekCE/Geotrek-admin

.. |master-e2e| image::
    https://img.shields.io/endpoint?url=https://dashboard.cypress.io/badge/simple/ktpy7v/master&style=flat&logo=cypress
    :alt: End to End
    :target: https://dashboard.cypress.io/projects/ktpy7v/runs

.. |master-rtd| image::
    https://readthedocs.org/projects/geotrek/badge/?version=latest&style=flat
    :alt: Documentation
    :target: https://geotrek.readthedocs.io


In brief
--------

* Web mapping application offering GIS features
* Manage paths, interventions, signage, treks, POIs, touristic events and so much more
* Track maintenance of equipments and infrastructures
* Control objets by district, protected areas, physical and legal status of paths
* Compute 3D attributes using DEM draping
* Allow to interconnect with multiple applications to synchronize data (Suricate, Apidae, Tourinsoft, etc.)
* Publish a public website with `Geotrek-rando <https://github.com/GeotrekCE/Geotrek-rando-v3>`_ (e.g. `PNE <https://rando.ecrins-parcnational.fr>`_, `PNM-PNAM <https://destination.marittimemercantour.eu/>`_)
* Publish a public mobile application with `Geotrek-mobile <https://github.com/GeotrekCE/Geotrek-mobile>`_ (e.g. `OTGC <https://play.google.com/store/apps/details?id=io.geotrek.grandcarcassonne>`_, `CD39 <https://apps.apple.com/app/jura-outdoor/id6446137384>`_)

.. image:: http://geotrek.fr/assets/img/screen-1.png

More information on product website http://geotrek.fr

Documentation
-------------

* `User manual (in french) <https://geotrek.readthedocs.io/en/latest/usage/overview.html>`_
* `Installation and configuration instructions <http://geotrek.readthedocs.org>`_
* Help us translate `on Weblate <https://weblate.makina-corpus.net/>`_


Contribution
------------

* `Contributing guide <https://geotrek.readthedocs.io/en/master/CONTRIBUTING.html>`_
* `Development documentation <https://geotrek.readthedocs.io/en/master/contribute/development.html>`_


License
-------

* OpenSource - BSD
* Copyright (c) 2012-2023 - Makina Corpus / Parc national des Ecrins - Parc National du Mercantour - Parco delle Alpi Marittime

.. image:: https://geotrek.fr/assets/img/logo_makina.svg
    :target: https://territoires.makina-corpus.com/
    :width: 170

.. image:: https://geotrek.fr/assets/img/logo_autonomens-h120m.png
    :target: https://datatheca.com

----

.. image:: http://geotrek.fr/assets/img/parc_ecrins.png
    :target: http://www.ecrins-parcnational.fr


.. image:: http://geotrek.fr/assets/img/parc_mercantour.png
    :target: http://www.mercantour.eu


.. image:: http://geotrek.fr/assets/img/alpi_maritime.png
    :target: http://www.parcoalpimarittime.it


Status of sub-projects
----------------------

* |django-mapentity| `django-mapentity <https://github.com/makinacorpus/django-mapentity>`_
* |django-leaflet| `django-leaflet <https://github.com/makinacorpus/django-leaflet>`_
* |convertit| `ConvertIt <https://github.com/makinacorpus/convertit>`_
* |Leaflet.GeometryUtil| `Leaflet.GeometryUtil <https://github.com/makinacorpus/Leaflet.GeometryUtil>`_
* |Leaflet.FileLayer| `Leaflet.FileLayer <https://github.com/makinacorpus/Leaflet.FileLayer>`_
* |Leaflet.AlmostOver| `Leaflet.AlmostOver <https://github.com/makinacorpus/Leaflet.AlmostOver>`_

.. |django-mapentity| image:: https://github.com/makinacorpus/django-mapentity/actions/workflows/python-ci.yml/badge.svg
    :target: https://github.com/makinacorpus/django-mapentity/actions/workflows/python-ci.yml

.. |django-leaflet| image:: https://github.com/makinacorpus/django-leaflet/actions/workflows/python-app.yml/badge.svg
    :target: https://github.com/makinacorpus/django-leaflet/actions/workflows/python-app.yml

.. |convertit| image:: https://circleci.com/gh/makinacorpus/convertit.svg?style=shield
    :target: https://circleci.com/gh/makinacorpus/convertit

.. |Leaflet.GeometryUtil| image:: https://travis-ci.org/makinacorpus/Leaflet.GeometryUtil.png?branch=master
    :target: https://travis-ci.org/makinacorpus/Leaflet.GeometryUtil?branch=master

.. |Leaflet.FileLayer| image:: https://travis-ci.org/makinacorpus/Leaflet.FileLayer.png?branch=master
    :target: https://travis-ci.org/makinacorpus/Leaflet.FileLayer?branch=master

.. |Leaflet.AlmostOver| image:: https://travis-ci.org/makinacorpus/Leaflet.GeometryUtil.png?branch=master
    :target: https://travis-ci.org/makinacorpus/Leaflet.AlmostOver?branch=master
