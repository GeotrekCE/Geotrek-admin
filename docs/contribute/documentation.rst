Documentation
=============

We use sphinx doc and `sphinx-immaterial theme <https://jbms.github.io/sphinx-immaterial/>`_. Requirements are included.

A container with documentation instance is created thanks to sphinx-autobuild.

To watch and test documentation on local environment, run:

.. code-block:: bash

    make serve_docs

Access to documentation built in html : http://0.0.0.0:8800

To test documentation build, run:

.. code-block:: bash

    make build_docs


Translate documentation
-----------------------

- Update documentation translation files

.. code-block:: bash

    make build_doc_translations
