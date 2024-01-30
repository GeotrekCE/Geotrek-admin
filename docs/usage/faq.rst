==========================
Frequently asked questions
==========================

.. contents::
   :local:
   :depth: 2

How are 3D informations obtained ?
----------------------------------

All paths geometries are *"draped"* on a Digital Elevation Model, when created
or updated.

All linear objects that defined using topologies (*treks, ...*) take their 3D informations
from their related paths, instead of reading the DEM.


How is the ascent computed on treks ?
-------------------------------------

We compute the `cumulative elevation gain <http://en.wikipedia.org/wiki/Cumulative_elevation_gain>`_.

We sample the DEM every 25m by defaut (see ``ALTIMETRIC_PROFILE_PRECISION`` setting),
and we add some smoothing to avoid noise.

For more details :

* `The smoothing explanation <https://github.com/GeotrekCE/Geotrek-admin/issues/840#issuecomment-30229813>`_
* `The piece of code to compute positive and negative accumulations <https://github.com/GeotrekCE/Geotrek-admin/blob/v0.27.2/geotrek/altimetry/sql/00_utilities.sql#L113-L132>`_
* `Draping lines with PostGIS <http://blog.mathieu-leplatre.info/drape-lines-on-a-dem-with-postgis.html>`_
  (or `french version <http://makina-corpus.com/blog/metier/2013/draper-des-lignes-sur-un-mnt-avec-postgis>`_)

How are POIs related to treks ?
-------------------------------

POIs are considered as an *editorial* information, and are created carefully
along treks.

When a POI is created, it is attached to the closest path.

A trek is defined by a serie of paths, and some POIs are associated to them.

.. note ::

    There is currently no way to manually control the association between
    treks and POIs.

    This was discussed among the first *Geotrek* users, come and argue on the mailing
    list !


If ``TREKKING_TOPOLOGY_ENABLED`` is set to ``False``, there are no paths involved.
POIs are thus related to treks using a basic spatial intersection, with a
distance set in setting ``TREK_POI_INTERSECTION_MARGIN`` (default to 500 meters).


Can I have overlapping districts ?
----------------------------------

Districts are a generic notion to qualify your territory. They can be valleys,
mounts, ...

You can imagine using the districts table for all those different notions,
resulting in overlapping geometries. Geotrek-admin will associate them all to your
objects.


Why does Makina Corpus sell Geotrek, released under an Open-Source license ?
----------------------------------------------------------------------------

In the early years of the Free Software movement, it was quite common to pay
in order to receive a physical copy (on floppy disks) of some GNU programs and source
code.

In the late nineties, the IT industry was not confortable with the confusion
introduced by the word *Free* in English ("free" as freedom, or "free" as costless), and
therefore started to spread the word *Open Source* instead.

Today, those copies of Open Source software can be obtained on the Internet for free
of course. But yet, the GNU Software Fundation `still recommends to claim a financial contribution <https://www.gnu.org/philosophy/selling.en.html>`_ when
distributing them, in order to support the development and maintenance. And note that nowadays,
many of the most important Open Source applications have their own fundation, focused on
collecting funds for development and maintenance.

The *Geotrek fundation* does not exist yet, but the community is growing. Makina Corpus
is currently maintaining this Open Source application, which implies the following
responsabilities :

* Maintain a public website, with a fully working demo ;
* Write documentation ;
* Provide community support on the mailing-list ;
* Promote the application at conferences, social networks and communities ;
* Triage and investigate issues tickets on Github ;
* Fix bugs and regressions if any ;
* Contribute, propose and argue code merge on external libraries ;
* Keep software dependencies up-to-date, without regressions ;
* Make sure the application remains easy to install on latest Linux distributions ;
* Add some engineering to allow customization and pluggability when new specific features are planned ;

Each of these tasks are often considered implicit, but they consume energy and time,
which represents a substantial cost for a company like ours.

To conclude, we don't really sell *Geotrek*, since you can get it on Github and install it easily, but
we ask for a financial contribution regarding the above responsabilities. It is not only legal, but also recommended by the funders of the Free and Open Source Software movement.

How can I help and contribute ?
-------------------------------

There are many ways to contribute to a Free Software. And modifying
the source code is probably the least common action. For example :

* Help the users and answers questions on the `mailing-list <https://groups.google.com/g/geotrek-fr>`_ ;
* Download it, try it ;
* `Open a ticket <https://github.com/GeotrekCE/Geotrek-admin/issues/new>`_ when you encounter a bug ;
* `Open a ticket <https://github.com/GeotrekCE/Geotrek-admin/issues/new>`_ when you have a suggestion or feature idea ;
* Share your feedback, spread the word inside your organization ;
* Write and talk about *Geotrek*, at conferences, workgroups, forums ;
* Translate the documentation ;
* Translate the menus, buttons and labels (we use `Weblate <https://weblate.makina-corpus.net>`_) ;
* Maintain the installation script for different Linux distributions (*requires some basic Linux skills*) ;
* Fix bugs or improve layout and apparence (*requires Webmaster skills*) ;
* Fix bugs or improve core modules (*requires python/Django skills*).

Join us on the `mailing list <https://groups.google.com/forum/#!forum/geotrek-fr>`_! Send an email to ``geotrek-fr+subscribe@googlegroups.com``
and you will receive an invitation automatically :)
