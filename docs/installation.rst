============
INSTALLATION
============

These instructions will install *Geotrek* on a dedicated server for production.
For a developer instance, please follow  :ref:`the dedicated procedure <development-section>`.

Requirements
------------

* Ubuntu Server 18.04 Bionic Beaver (http://releases.ubuntu.com/18.04/) or
  Ubuntu Server 16.04 Xenial Xerus (http://releases.ubuntu.com/16.04/)


A first estimation on system resources is :

* 4 Go RAM
* 20 Go disk space


Installation
------------

Once the OS is installed (basic installation, with OpenSSH server), log in with your linux user (not root). 
You will also need unzip and wget (``sudo apt-get install unzip wget``).

Make sure you are in the user folder :

::

    cd /home/mylinuxuser

Download the latest version of Geotrek-admin with the following commands (X.Y.Z to replace 
with the latest stable version number : https://github.com/GeotrekCE/Geotrek-admin/releases) :

::

    wget https://github.com/GeotrekCE/Geotrek-admin/archive/X.Y.Z.zip

Unzip the archive of Geotrek-admin

::

    unzip Geotrek-admin-X.Y.Z.zip
    
You can rename Geotrek-admin-X.Y.Z folder to Geotrek-admin

Go into Geotrek-admin folder and launch its installation

::

    cd Geotrek-admin
    ./install.sh

You will be prompt for editing the base configuration file (``.env``),
using the default editor.

:notes:

    In order to use a remote server (*recommended*), set the appropriate values
    for the connection.
    The connection must be operational (it will be tested during install).


To make sure the application runs well after a reboot, try now : ``sudo reboot``.
And access the application ``http://yourserver/``.

You will be prompted for login, jump to :ref:`loading data section <loading data>`,
to create the admin user and fill the database with your data!


Software update
---------------

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
    systemctl stop geotrek

Deploy the new version :

::
    cd /path/to/your/geotrek
    ./update.sh

Check the version on the login page !


:note:

    Shutting down the current instance may not be necessary. But this allows us to
    keep a generic software update procedure.

    If you don't want to interrupt the service, skip the ``stop`` step, at your own risk.


Check out the :ref:`troubleshooting page<troubleshooting-section>` for common problems.


Server migration from non docker version
----------------------------------------

It is a new installation with an additional backup/restore and a file transfert
in between. The commands below are examples to adapt to your actual configuration
(server names, database configuration).

Take care of your current geotrek version, you need to have latest non docker version installed :

2.21.0

Backup settings, media files and database on the old server:

::

    cd Geotrek
    sudo -u postgres pg_dump -Fc geotrekdb > geotrekdb.backup
    tar cvzf data.tgz geotrekdb.backup bulkimport/parsers.py var/static/ var/media/paperclip/ var/media/upload/ var/media/templates/ etc/settings.ini geotrek/settings/custom.py

Get and unzip Geotrek sources on the new server:

::

    wget https://github.com/GeotrekCE/Geotrek-admin/archive/2.xx.x.zip
    unzip 2.xx.x.zip
    mv Geotrek-2.0.0 Geotrek
    cd Geotrek

Restore files on the new server:

::

    scp old_server:Geotrek/data.tgz .
    tar xvzf data.tgz

Then edit `etc/settings.ini` to update host variable and `geotrek/settings/custom.py`
to update IGN key.

Install Geotrek on the new server:

::

    ./install.sh

Restore database on the new server:

::
    sudo systemctl stop geotrek
    mv geotrekdb.backup var/geotrekdb.backup
    pg_restore -d geotrekdb geotrekdb.backup
    docker-compose run web update.sh
    sudo systemctl start geotrek
