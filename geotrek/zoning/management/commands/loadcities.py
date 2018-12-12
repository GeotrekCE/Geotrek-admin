# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis.gdal import DataSource, GDALException
from geotrek.zoning.models import *
from django.contrib.gis.geos.polygon import Polygon
from django.contrib.gis.geos.collections import MultiPolygon
from django.conf import settings


class Command(BaseCommand):
    help = 'Load Cities from a file within the spatial extent\n'

    def add_arguments(self, parser):
        parser.add_argument('cities')
        parser.add_argument('--code-attribute', '-c', action='store', dest='code', default='code',
                            help="Name of the code's attribute inside the file")
        parser.add_argument('--name-attribute', '-n', action='store', dest='name', default='nom',
                            help="Name of the name's attribute inside the file")
        parser.add_argument('--encoding', '-e', action='store', dest='encoding', default='utf-8',
                            help='File encoding, default utf-8')
        parser.add_argument('--srid', '-s', action='store', dest='srid', default=4326,
                            help="File's SRID")

    def handle(self, *args, **options):
        verbosity = options.get('verbosity')
        file = options.get('cities')
        name = options.get('name')
        code = options.get('code')
        encoding = options.get('encoding')
        srid = options.get('srid')
        bbox = Polygon.from_bbox(settings.SPATIAL_EXTENT)
        bbox.srid = settings.SRID
        ds = DataSource(file)

        for layer in ds:
            for feat in layer:
                try:
                    geom = feat.geom.geos
                    if isinstance(geom, Polygon):
                        geom = MultiPolygon(geom)
                        if not geom.srid:
                            geom.srid = srid

                        if geom.srid != settings.SRID:
                            try:
                                geom.transform(settings.SRID)
                            except GDALException:
                                raise CommandError("SRID is not well configurate, change/add option srid")

                        geom.dim = 2
                        if geom.within(bbox):
                            city, created = City.objects.update_or_create(code=feat.get(code),
                                                                          name=feat.get(name).encode(encoding),
                                                                          geom=geom)
                            if verbosity > 1:
                                if created:
                                    self.stdout.write("Created %s" % feat.get(name))
                                elif verbosity > 1:
                                    self.stdout.write("Updated %s" % feat.get(name))
                    else:
                        self.stdout.write("%s's geometry is not a polygon" % feat.get(name))
                except UnicodeEncodeError as exc:
                    self.stdout.write("Problem of encoding with %s" % feat.get(name))
