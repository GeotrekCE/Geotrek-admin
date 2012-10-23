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
    def test_split_tee_1(self):
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

    def test_split_tee_2(self):
        """
        CD exists. Add AB.
        """
        cd = PathFactory.create(geom=LineString((2,0,0),(2,2,0)))
        self.assertEqual(cd.length, 2)
        ab = PathFactory.create(name="AB", geom=LineString((0,0,0),(4,0,0)))
        
        # Make sure AB was split :
        self.assertEqual(ab.geom, LineString((0,0,0),(2,0,0)))
        self.assertEqual(ab.length, 2)  # Length was also updated
        
        clones = Path.objects.filter(name="AB").exclude(pk=ab.pk)
        ab_2 = clones[0]
        self.assertEqual(ab_2.geom, LineString((2,0,0),(4,0,0)))
        self.assertEqual(ab_2.length, 2)  # Length was also updated

    def test_split_cross(self):
        """
               C
               +
               |
        A +----+----+ B
               |
               +      AB exists. Add CD.
               D      
        """
        ab = PathFactory.create(name="AB", geom=LineString((0,0,0),(4,0,0)))
        cd = PathFactory.create(name="CD", geom=LineString((2,-2,0),(2,2,0)))
        ab.reload()
        ab_2 = Path.objects.filter(name="AB").exclude(pk=ab.pk)[0]
        cd_2 = Path.objects.filter(name="CD").exclude(pk=cd.pk)[0]
        self.assertEqual(ab.geom, LineString((0,0,0),(2,0,0)))
        self.assertEqual(cd.geom, LineString((2,-2,0),(2,0,0)))
        self.assertEqual(ab_2.geom, LineString((2,0,0),(4,0,0)))
        self.assertEqual(cd_2.geom, LineString((2,0,0),(2,2,0)))

    def test_split_on_update(self):
        """
        
               + E

        A +----+----+ B

        C +----+ D    AB and CD exist. CD updated into CE.
        
        """
        ab = PathFactory.create(name="AB", geom=LineString((0,0,0),(4,0,0)))
        cd = PathFactory.create(name="CD", geom=LineString((0,-2,0),(2,-2,0)))
        ab.reload()
        self.assertEqual(ab.length, 4)
        self.assertEqual(cd.length, 2)
        
        cd.geom = LineString((0,-2,0),(2,-2,0), (2,2,0))
        cd.save()
        ab.reload()
        self.assertEqual(ab.length, 2)
        self.assertEqual(cd.length, 4)
        ab_2 = Path.objects.filter(name="AB").exclude(pk=ab.pk)[0]
        cd_2 = Path.objects.filter(name="CD").exclude(pk=cd.pk)[0]
        self.assertEqual(ab_2.length, 2)
        self.assertEqual(cd_2.length, 2)

    def test_split_twice(self):
        """
        
             C   D
             +   +
             |   |
        A +--+---+--+ B
             |   |
             +---+ 
        
        """
        ab = PathFactory.create(name="AB", geom=LineString((0,0,0),(4,0,0)))
        cd = PathFactory.create(name="CD", geom=LineString((1,2,0),(1,-2,0),
                                                           (3,-2,0),(3,2,0)))
        ab.reload()
        self.assertEqual(ab.length, 1)
        self.assertEqual(cd.length, 2)
        ab_clones = Path.objects.filter(name="AB").exclude(pk=ab.pk)
        cd_clones = Path.objects.filter(name="CD").exclude(pk=cd.pk)
        self.assertEqual(len(ab_clones), 2)
        self.assertEqual(len(cd_clones), 2)
        self.assertEqual(ab_clones[0].geom, LineString((1,0,0),(3,0,0)))
        self.assertEqual(ab_clones[1].geom, LineString((3,0,0),(4,0,0)))
        
        self.assertEqual(cd_clones[0].geom, LineString((1,0,0),(1,-2,0),
                                                       (3,-2,0),(3,0,0)))
        self.assertEqual(cd_clones[1].geom, LineString((3,0,0),(3,2,0)))
