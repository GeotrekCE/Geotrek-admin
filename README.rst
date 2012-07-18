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

============
INITIAL DATA
============

Load path data with the following command::

    bin/django loaddata data/pathes.pne.json

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
