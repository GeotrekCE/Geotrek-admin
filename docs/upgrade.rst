===============
Software update
===============

WARNING:

Intermediate versions are required to upgrade your instance.

If your version is < 2.13.1, you need to install this version.

If your version is < 2.16.2, you need to install this version

All versions are published on `the Github forge <https://github.com/GeotrekCE/Geotrek-admin/releases>`_.
Download and extract the new version in a separate folder (**recommended**).

.. code-block:: bash

    wget https://github.com/GeotrekCE/Geotrek-admin/archive/X.Y.Z.zip
    unzip X.Y.Z.zip
    cd Geotrek-X.Y.Z/

Before upgrading, **READ CAREFULLY** the release notes, either from the ``docs/changelog.rst``
files `or online <https://github.com/GeotrekCE/Geotrek-admin/releases>`_.

Shutdown previous running version :

::

    # Shutdown previous version
    sudo supervisorctl stop all


Copy your old configuration and uploaded files to your new folder.

::

    # Configuration files
    cp -aR ../previous-version/etc/ .

    # Uploaded files
    cp -aR ../previous-version/var/ .

    # If you have advanced settings
    cp ../previous-version/geotrek/settings/custom.py geotrek/settings/custom.py

    # If you have import parsers
    cp ../previous-version/bulkimport/parsers.py bulkimport/parsers.py

    # If you have custom translations
    cp -aR ../previous-version/geotrek/locale/ geotrek/

Deploy the new version :

::

    # Re-run install
    ./install.sh

    # Empty cache
    sudo service memcached restart


Check the version on the login page !

:note:

    Shutting down the current instance may not be necessary. But this allows us to
    keep a generic software update procedure.

    If you don't want to interrupt the service, skip the ``stop`` step, at your own risk.

Check out the :ref:`troubleshooting page<troubleshooting-section>` for common problems.