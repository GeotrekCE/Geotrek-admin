Documentation
=============

We use sphinx doc and sphinx-rtd-theme. Requirements are included.

To compile and test documentation on local environment, run :

.. code-block :: bash

    docker-compose run --workdir /opt/geotrek-admin/docs --rm web make html
