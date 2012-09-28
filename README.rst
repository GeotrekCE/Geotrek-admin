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

Once the OS is installed (basic installation, with OpenSSH server), copy and extract the source archive.

Go into the extracted directory, just follow the installation process :

::

	chmod +x install.sh
    ./install.sh

You will mainly be prompt for editing the base configuration file (``settings.ini``),
using *Vim* (Finish with 'Esc' then ':wq' to save and quit).

To make sure the application runs well after a reboot, try now : reboot. And
access the ``http://yourserver/``.

See information below for configuration and loading initial demonstration data.


Software update
---------------

Keep previous versions in separate folders (**recommended**) :

::

	# Copy previous settings
	cp ../previous-version/etc/settings.ini  etc/settings.ini
	
	# Re-run install
    ./install.sh


Or instead, if you prefer, you can overwrite the source code (or use symlinks), 
and run ``./install.sh``.


Load MNT raster
---------------

::

    bin/django loaddem <PATH>/w001001.adf


:note:

    This command makes use of *GDAL* and ``raster2pgsql`` internally. It
    therefore supports all GDAL raster input formats. You can list these formats
    with the command ``raster2pgsql -G``.


Initial Data
------------

Load example data (used in development) :

::

    make load_data


Among other things, an administrator "admin"/"admin" will be created.


Without Initial Data
--------------------

If you do not load data, you'll have to at least create a super user :

::

    bin/django createsuperuser --username=admin --email=admin@corp.com

or change its password : 

::

    bin/django changepassword --username admin <password>


=============
CONFIGURATION
=============


Configuration update
--------------------

After editing ``etc/settings.ini``, refresh the running instance with :

::

    make deploy


External authent
----------------

You can authenticate user against a remote database table or view.

To enable this feature, fill *authent_dbname* and other fields in ``etc/settings.ini``.

Expected columns in table/view are : 

* username : string (*unique*)
* first_name : string
* last_name : string
* password : string (simple md5 encoded, or full hashed and salted password)
* email : string
* level : integer (1: readonly, 2: redactor, 3: path manager, 4: trekking manager, 6: administrator)
* structure : string
* lang : string (language code)


:notes:

    User management will be disabled from Administration backoffice.

    In order to disable remote login, just remove *authent_dbname* value in settings
    file, and update instance (see paragraph above).
    
    Caminae can support many types of users authentication (LDAP, oauth, ...), contact-us
    for more details.

:note:

    This command makes use of ``GDAL`` and ``raster2pgsql`` internally. It
    therefore supports all GDAL raster input formats. You can list these formats
    with the command ``raster2pgsql -G``.


===========
DEVELOPMENT
===========

For code contributors only : in order to run a development instance :

::

    ./install.sh --dev

Start local instance :

::

    make serve


Run unit tests :

::

    make tests

For PDF conversion server, run an instance in a separate terminal :

::

    bin/pserve src/topdfserver/development.ini

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
