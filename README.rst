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


==================
DEFINITION OF DONE
==================

Before setting a story to `DONE`, make sure : 

* Docstrings were added/updated to your code
* Unit tests of core behaviours are up to date
* Functional tests were added in `docs/functional-tests.rst`
* Installation and settings management is up to date
* No error in CI

Check TODO in the source tree ::

    find . | xargs egrep -n -i '(TODO|temporary)'

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
