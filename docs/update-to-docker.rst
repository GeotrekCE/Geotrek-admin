================
UPDATE TO DOCKER
================

These instructions will update *Geotrek* on a dedicated server with docker for production from a previous install
without docker.

First you should update at least to version 2.22.0 without docker.
Please folow this documentation :

WARNING:

Intermediate versions are required to upgrade your instance,

If your version is < 2.13.1, you need to install this version.

If your version is < 2.16.2, you need to install this version


Server migration docker
-----------------------

Follow the installation : ``docs/installation-docker.rst``
Do not forget to create the server in another folder and stop postgresql :
::
    sudo service stop postgresql


Move your different settings/datas in the new folder
::
    # Uploaded files
    cp -aR ../previous-version/var ./var

    # If you have advanced settings
    cp ../previous-version/geotrek/settings/custom.py ./var/conf/custom.py

    # If you have import parsers
    cp ../previous-version/bulkimport/parsers.py ./var/conf/parsers.py

    # If you have custom translations
    cp -aR ../previous-version/geotrek/locale/ ./var/conf/extra_locale/

    # If you have custom templates (example)
    cp ../previous-version/geotrek/trekking/templates/trekking/trek_public_pdf.html ./var/conf/extra_templates/

Then you can run your geotrek : ````

Then you can upgrade your docker to new versions : ``docs/upgrade-docker.rst``
