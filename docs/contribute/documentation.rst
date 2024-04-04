Documentation
=============
.. contents::
   :local:
   :depth: 2

We use sphinx doc and sphinx-rtd-theme. Requirements are included.

A container based on sphinx image is created using ``docker-compose-dev.yml``,
documentation is built in watch mode thanks to sphinx-autobuild.

To compile and test documentation on local environment, run:

.. code-block:: bash

    docker-compose up -d sphinx


Access to documentation built in html : http://0.0.0.0:8800


Translate documentation
-----------------------

- Generate ``.pot`` files if needed

.. code-block:: python

    docker-compose run --rm sphinx make gettext

- Generate ``.po`` files

.. code-block:: python

    docker-compose run --rm sphinx sphinx-intl update -p _build/locale -l fr
