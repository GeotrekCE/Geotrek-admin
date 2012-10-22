# -*- coding: utf-8 -*-
from django.test import TestCase
from django.conf import settings
from django.utils import simplejson
from django.contrib.gis.geos import Point, LineString
from django.db import connections, DEFAULT_DB_ALIAS, IntegrityError

from caminae.mapentity.tests import MapEntityTest
from caminae.common.utils import dbnow, almostequal
from caminae.authent.factories import UserFactory, PathManagerFactory, StructureFactory
from caminae.authent.models import Structure, default_structure
from caminae.core.factories import (PathFactory, PathAggregationFactory, 
    TopologyFactory, StakeFactory, TrailFactory, ComfortFactory)
from caminae.core.models import Path, Topology, PathAggregation





class SplitPathTest(TestCase):
    def test_split_tee(self):
        """
               C
        A +----+----+ B
               |
               +      AB exists. Add CD.
               D      
        """
        ab = PathFactory.create(name="AB", geom=LineString((0,0,0),(4,0,0)))
        self.assertEqual(ab.length, 4)
        cd = PathFactory.create(geom=LineString((2,0,0),(2,2,0)))
        self.assertEqual(cd.length, 2)
        
        # Make sure AB was split :
        ab.reload()
        self.assertEqual(ab.geom, LineString((0,0,0),(2,0,0)))
        self.assertEqual(ab.length, 2)  # Length was also updated
        # And a clone of AB was created
        clones = Path.objects.filter(name="AB").exclude(pk=ab.pk)
        self.assertEqual(len(clones), 1)
        ab_2 = clones[0]
        self.assertEqual(ab_2.geom, LineString((2,0,0),(4,0,0)))
        self.assertEqual(ab_2.length, 2)  # Length was also updated

"""


    Tests
    .....

    Cas 1a::

               C
        A +----+----+ B
               |
               +      Troncon AB existant,
               D      ajout du troncon CD.

    Cas 1b::

        Même schéma, mais le troncon CD est existant et on ajoute le troncon AB.

    Cas 2::

               C
               +
               |
        A +----+----+ B
               |
               +      Troncon AB existant,
               D      ajout du troncon CD.

    Cas 3::

               + E

        A +----+----+ B

        C +----+      Troncons AB et CD existant,
               D      la géométrie de CD est modifiée en CDE.

    Cas 4::

             C   D
             +   +
             |   |
        A +--+---+--+ B
             |   |
             +---+    Troncon AB existant,
                      ajout du troncon CD.


"""
