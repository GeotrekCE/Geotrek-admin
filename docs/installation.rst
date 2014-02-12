============
INSTALLATION
============

These instructions will install *Geotrek* on a dedicated server for production.
For a developer instance, please follow  :ref:`the dedicated procedure <development-section>`.

Requirements
------------

* Ubuntu Server 12.04 Precise Pangolin (http://releases.ubuntu.com/12.04/)


A first estimation on system resources is :

* 1 Go RAM
* 10 Go disk space


Installation
------------

Once the OS is installed (basic installation, with OpenSSH server), copy the ``install.sh`` file
or extract the source archive.

Go into the extracted directory, just follow the installation process :

::

    ./install.sh

You will be prompt for editing the base configuration file (``settings.ini``),
using the default editor. (With *Vim*, finish with 'Esc' then ':wq' to save and quit).

:notes:

    If you leave *localhost* for the database host (``dbhost`` value), a
    Postgresql with PostGis will be installed locally.
    In order to use a remote server (*recommended*), set the appropriate value.
    The connection must be operational (it will be tested during install).

To make sure the application runs well after a reboot, try now : ``sudo reboot``.
And access the application ``http://yourserver/``.

See information below for configuration and loading initial demonstration data.


Software update
---------------

Keep previous versions in separate folders (**recommended**).

First, copy your old configuration and uploaded files to your new folder.

::

    # Configuration files
    mkdir -p etc/
    cp ../previous-version/etc/settings.ini etc/
    # Uploaded files
    mkdir -p var/
    cp -R ../previous-version/var/tiles var/tiles
    cp -R ../previous-version/var/media var/media


Shutdown previous running version, and run install :

::

    # Shutdown previous version
    ../previous-version/bin/supervisorctl stop all
    sudo service supervisor stop

    # Re-run install
    ./install.sh

    # Reload configuration
    sudo service supervisor restart

    # Empty cache
    sudo service memcached restart

:note:

    Shutting down current instead may not be necessary. But this allows us to keep a generic software update procedure.


Tips and Tricks
---------------

* Use symlinks for uploaded files and cached tiles to avoid duplicating them on disk:

::

    mv var/tiles ~/tiles
    ln -s ~/tiles `pwd`/var/tiles

    mv var/media ~/media
    ln -s ~/media `pwd`/var/media


* Speed-up upgrades by caching downloads :

::

    mkdir ~/downloads
    mkdir  ~/.buildout

Create ``/home/sentiers/.buildout/default.cfg`` with ::

    [buildout]
    download-cache = /home/sentiers/downloads
