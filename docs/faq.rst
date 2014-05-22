==========================
FREQUENTLY ASKED QUESTIONS
==========================

How 3D informations are obtained ?
----------------------------------

All paths geometries are *"draped"* on a Digital Elevation Model, when created
or updated.

All linear objects that defined using topologies (*treks, ...*) take their 3D informations
from their related paths, instead of reading the DEM.


How POIs are related to treks ?
-------------------------------

POIs are considered as an *editorial* information, and are created carefully
along treks.

When a POI is created, it is attached to the closest path.

A trek is defined by a serie of paths, and some POIs are associated to them.

:notes:

    There is currently no way to manually control the association between
    treks and POIs.

    This was discussed among the first *Geotrek* users, come and argue on the mailing
    list !
