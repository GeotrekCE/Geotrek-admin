*Caminae*, a National Park Manager :)

=====
SETUP
=====

Requirements
------------

* Ubuntu Server 12.04 Precise Pangolin (http://releases.ubuntu.com/12.04/)


A first estimation on system resources is :

* 1 Go RAM
* 10 Go disk space


Installation
------------

Once the OS is installed, copy and extract the source archive.

Follow the installation process :

::

    ./install.sh


You will mainly be prompt for editing the base configuration file (``settings.ini``).

To make sure the application runs well after a reboot, try now : reboot. And
access the ``http://yourserver/``.

See paragraph below for loading initial demonstration data.


Software update
---------------

Overwrite the source code (or use symlinks), and run :

::

    make deploy


Initial Data
------------

Load example data (used in development) :

::

    make load_data


Among other things, an administrator "admin"/"admin" will be created.


Without Initial Data
--------------------

Create a super user manually :

::

    bin/django createsuperuser --username=admin --email=admin@corp.com

or change its password : 

::

    bin/django changepassword --username admin <password>


Load MNT raster
---------------

::

    bin/django loaddem <PATH>/mnt_0_ecrins/w001001.adf


===========
DEVELOPMENT
===========

In order to run a development instance :

::

    ./install.sh --dev

Start local instance :

::

    make serve


Run unit tests :

::

    make tests


=======
AUTHORS
=======

    * Gilles Bassière
    * Sylvain Beorchia
    * Mathieu Leplatre
    * Anaïs Peyrucq
    * Satya Azemar
    * Simon Thépot

|makinacom|_

.. |makinacom| image:: http://depot.makina-corpus.org/public/logo.gif
.. _makinacom:  http://www.makina-corpus.com


=======
LICENSE
=======

    * (c) Makina Corpus
