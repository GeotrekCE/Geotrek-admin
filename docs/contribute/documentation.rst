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

1. **Install the extension**::

       pip install sphinx-design

2. **Enable the extension** in ``docs/conf.py``:

   Example::

       extensions = [
           "sphinx-design",
       ]

3. **Add the extension to** ``requirements.in``:

   Example::

       sphinx-design

4. **Recompile** ``requirements.txt``::

       pip-compile requirements.in -o requirements.txt

5. **Build the documentation** (using Docker)::

       docker compose build

6. **Serve the documentation locally**::

       make serve_docs


Translate documentation
-----------------------

- Update documentation translation files

.. code-block:: bash

    make build_doc_translations
