*caminae*, national park manager :)

=====
SETUP
=====

Run development server :

::

    ./install.sh --dev
    make serve

Run tests :

::

    make tests

==========
DEPLOYMENT
==========

::

    ./install.sh

Create a super user :

::

    bin/django createsuperuser --username=admin --email=admin@corp.com

or change its password : 

::

    pbin/django changepassword --username admin <password>


Initial Data
------------

Load example data (used in development) :

::

    make load_data


=======
AUTHORS
=======

    * Gilles Bassière
    * Sylvain Beorchia
    * Mathieu Leplatre
    * Anaïs Peyrucq
    * Simon Thépot

|makinacom|_

.. |makinacom| image:: http://depot.makina-corpus.org/public/logo.gif
.. _makinacom:  http://www.makina-corpus.com


=======
LICENSE
=======

    * (c) Makina Corpus
