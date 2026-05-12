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

Add extension
--------------

Follow these steps to add the ``sphinx-design`` extension to the documentation:

1. **Enable the extension** in ``docs/conf.py``:

   Example::

       extensions = [
           "new-extension",
       ]

2. **Add the extension to** ``requirements.in``:

   Example::

       new-extension

3. **Generate the new requirements version** ``requirements.txt``::

       pip-compile requirements.in -o requirements.txt

4. **Build the documentation** to download the new package (using Docker)::

       docker compose build


Translate documentation
-----------------------

- Update documentation translation files

.. code-block:: bash

    make build_doc_translations
