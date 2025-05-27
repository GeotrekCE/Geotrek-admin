.. _installation:

============
Installation
============

Ubuntu package
==============

Use these instructions to install Geotrek-admin in an easy way on a dedicated Ubuntu Noble 24.04 or Jammy 22.04 LTS server for production.
For another distributions, please use :ref:`the Docker installation method <docker-section>`. It requires more technical skills.
Lastly, for a developer instance, please follow :ref:`the dedicated procedure <development-section>`.

Requirements
=============

Geotrek is mostly a CPU-bound application due to the complex queries including geometric operations (such as intersection)
which are executed on the database. This is especially true in the setup with a Geotrek Rando v3 portal requesting
dynamic geometric data through the Geotrek API.

In such a configuration the required system resources should be:

* 4 cores
* 8 Go RAM or more
* 50 Go disk space or more (20 Go + estimated size of attached files like photos, including elements imported from SIT)

If spreading the components on multiple hosts keep in mind the bottleneck will most likely be the CPU and RAM at the
database server level.

Software requirements are :

* Ubuntu Noble 24.04 LTS. Server flavor is recommended but any other flavors work too (desktop…)

An Internet connection with open HTTP and HTTPS destination ports is required.

Information to prepare before installation
===========================================

These information will be asked during the installation process and are the basic configuration of Geotrek-admin:

* The **domain name** or **IP** to use to access to **Geotrek-admin** web application.
* Rando server name: the **domain name** to use to access to **Geotrek-rando** website (optional, if appropriate).
* PostgreSQL **host, port, user, password and DB name** if you use an external DB server.
* The **SRID** of the projection to use to store geometries. The projection must match your geographic area and coordinates must be in meters.
* The list of **languages** into which translation of contents will be made
* The name or acronym of your **organization**

.. _fresh-installation:

Fresh installation
==================

Run the following command in a shell prompt on your server:

::

    bash -c "$(curl -fsSL https://raw.githubusercontent.com/GeotrekCE/Geotrek-admin/master/tools/install.sh)"

If you don't want to use a local database, you can run the following command instead.
This will prevent the script to install PostgreSQL server locally.
Don't forget to enable PostGIS extension in your remote database before installation.

::

    NODB=true bash -c "$(curl -fsSL https://raw.githubusercontent.com/GeotrekCE/Geotrek-admin/master/tools/install.sh)"

Then create the application administrator account and connect to the web interface.

.. md-tab-set::
    :name: create-superuser-command-tabs

    .. md-tab-item:: With Debian

         .. code-block:: python

          sudo geotrek createsuperuser

    .. md-tab-item:: With Docker

         .. code-block:: python
    
          docker compose run --rm web ./manage.py createsuperuser


If you are not confident with the ``install.sh`` script, or if you are having troubles, you can do the same operations by hand:

.. code-block:: bash

    sudo apt install curl ca-certificates
    sudo install -d /usr/share/geotrek
    sudo curl -o /usr/share/geotrek/apt.geotrek.org.key --fail https://packages.geotrek.fr/geotrek.gpg.key
    echo "deb [signed-by=/usr/share/geotrek/apt.geotrek.org.key] https://packages.geotrek.fr/ubuntu $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/geotrek.list
    sudo apt update

If you want to use a local database, install the pgRouting package by running:

.. code-block:: bash

    sudo apt install -y postgresql-pgrouting

You must create a user and its database, and enable `postgis`, `postgis_raster`, `pgrouting` and `pgcrypto` extensions before.

Install the Geotrek-admin package

.. code-block:: bash

    sudo apt install -y --no-install-recommends geotrek-admin postgis

.. note ::

    Geotrek-admin is automatically installed in ``/opt/geotrek-admin/`` directory.

    The installation automatically creates an internal ``geotrek`` linux user, owner of this directory

    The Geotrek-admin Python application is located in ``/opt/geotrek-admin/lib/python3.*/site-packages/geotrek`` directory

    PostGIS package, in combination with `--no-install-recommends`, include only scripts that are useful with `loaddem` command, not PostgreSQL server dependencies.

Extra steps
============

We highly recommend installing an antivirus software to regularly scan uploaded files located under ``/opt/geotrek-admin/var/media/``.

Here is the installation process for `ClamAV <https://www.clamav.net/>`_ :

::

   apt install clamav

Prepare quarantine folder for suspicious files :

::

   mkdir /var/lib/clamav/quarantine/
   chmod 700 /var/lib/clamav/quarantine/

Configure ClamAV via cron, to scan the folder once a day, put suspicious files in quarantine, and raise email alerts, by creating file ``/etc/cron.daily/clamscan`` with the following content :

::

   #!/bin/sh

   nice -n 15 ionice -c 3 clamscan --recursive --allmatch --suppress-ok-results --no-summary --infected --scan-mail=no --log=/var/log/clamav/scan-report.$(date -Iseconds) /opt/geotrek-admin/var/media/ |mail -E -s "ClamAV report for $(hostname)" admin@example.com

   # Cleanup old files in quarantine (> 90 days)
   find /var/lib/clamav/quarantine/ -type f -mtime +90 -delete

   # Cleanup old scan reports (> 365 days)
   find /var/log/clamav/ -type f -name "scan-report.*" -mtime +365 -delete


Make sure to change alert recepient (``admin@example.com`` above) and make this cron file executable :

::

   chmod 700 /etc/cron.daily/clamscan

If a suspicious file is put in quarantine, you will need to manually delete the corresponding attachment from Geotrek-Admin (since the file for this attachment has moved to the quarantine folder, it will no longer be found).

Uninstallation
===============

Run:

::

   apt-get remove geotrek-admin

Media files will be left in ``/opt/geotrek-admin/var`` directory. To remove them, run:

::

   apt-get purge geotrek-admin

To remove dependencies (convertit, screamshooter…), run:

::

   apt-get autoremove

.. note::

    PostgreSQL and its database will not be removed by these commands. If need be, remove them manually.

.. _docker-section:

Docker
=======

Docker installation allows to install several instances of Geotrek-admin on the same serveur,
and to install it on other distributions than Ubuntu.


1. Install Docker and Docker Compose, `from upstream packages <https://docs.docker.com/install/>`_
2. Download `zip package <https://github.com/GeotrekCE/Geotrek-admin/releases/latest/download/install-docker.zip>`_
3. Unzip the archive
4. Copy geotrek folder where you want (to keep compatibility with all examples in this documentation you can use `/opt/geotrek-admin` folder)
5. Copy ``.env.dist`` to ``.env`` and edit to feed your needs if necessary.
6. We recommend to use a specific user to run geotrek. So created it (useradd -m geotrek) and change ownership of the folder to this user.
   You should get UID and GID from this user and set them in .env file. With command ``id geotrek`` you should get uid and gid values.
7. If you use an external database, you should adapt your docker-compose to exclude postgres container and volume. Then, you should create user and database, enable PostGIS, Postgis_raster and pgcrypto extensions, then set dedicated environment variables in .env file (`POSTGRES_HOST` - empty if database installed on host, `POSTGRES_USER`, `POSTGRES_DATABASE` and `POSTGRES_PASSWORD`)
8. Run ``docker compose run --rm web update.sh``
9. Run ``docker compose up``
10. Install NGINX (or equivalent) and add a configuration file (taking inspiration from `nginx.conf.in`)

Management commands
====================

In documentation, replace ``sudo geotrek …`` commands by :

1. ``cd <install directory>``
2. ``docker compose run --rm web ./manage.py …``

Replace ``sudo dpkg-reconfigure geotrek-admin`` by :

1. ``cd <install directory>`` 
2. ``docker compose run --rm web update.sh``

Load fixtures
--------------

During the initial setup of Geotrek-admin, you may need to run certain commands to generate and load initial data (fixtures).

To load minimal fixtures, run this command **only once during setup**:

.. code::

  docker compose run --rm web load_data.sh

.. info::

  - The ``load_data.sh`` script is intended only for first-time installation. Never re-run this script after the initial installation, especially in a production environment. It will overwrite manually entered or modified data (e.g., paths, infrastructure, zoning, practices, etc.).

  - Do not run this command if your Geotrek instance does not use **dynamic segmentation**, as it will try to create segmentation-dependent data that may not be relevant or usable
  
  - Once your Geotrek instance is installed, you should import your own :ref:`initial data <minimal-initial-data>` to begin working with the application.

Create superuser
------------------

To create an application superuser, run this command :

.. code::

  docker compose run --rm web ./manage.py createsuperuser


