================
UPDATE TO DOCKER
================

These instructions will update *Geotrek* on a dedicated server with docker for production from a previous install
without docker.

First you should update at least to version 2.22.0 without docker.
Please folow this documentation if necessary : ``https://geotrek.readthedocs.io/en/2.22.1/installation.html#software-update``


Server migration docker
-----------------------

First, follow the installation : ``docs/installation.rst``, you can use your custom files from previous install
when you modify var/conf/custom.py and .env


Do not forget to create the instance in another folder and stop postgresql :

::

    sudo service stop postgresql


Move your different settings/datas in the new folder
::
    # If you have custom favicon, logo of login and header.
    cp ../previous-version/var/media/upload/favicon.png ./var/conf/extra_static/
    cp ../previous-version/var/media/upload/logo-login.png ./var/conf/extra_static/
    cp ../previous-version/var/media/upload/logo-header.png ./var/conf/extra_static/

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


You need to move the additional informations from settings.ini in var/conf/custom.py by hand.

    less etc/settings.ini
    editor var/conf/custom.py


Then you can run your geotrek :
::

    sudo systemctl restart geotrek

If you are Then you can upgrade your docker to new versions : ``docs/upgrade.rst``