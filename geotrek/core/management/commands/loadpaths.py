from django.contrib.gis.gdal import DataSource, GDALException, OGRIndexError
from geotrek.core.models import Path
from geotrek.authent.models import *
from django.contrib.gis.geos.collections import MultiLineString, Polygon, LineString
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Load Paths from a file within the spatial extent\n'

    def add_arguments(self, parser):
        parser.add_argument('paths', help="File's path of the paths")
        parser.add_argument('--structure', action='store', dest='structure', help="Define the structure")
        parser.add_argument('--name-attribute', '-n', action='store', dest='name', default='nom',
                            help="Name of the name's attribute inside the file")
        parser.add_argument('--comments-attribute', '-c', nargs='*', action='store', dest='comment',
                            help="")
        parser.add_argument('--encoding', '-e', action='store', dest='encoding', default='utf-8',
                            help='File encoding, default utf-8')
        parser.add_argument('--srid', '-s', action='store', dest='srid', default=4326,
                            help="File's SRID")
        parser.add_argument('--intersect', '-i', action='store_true', dest='intersect', default=False,
                            help="Check paths intersect spatial extent and not only within")

    def handle(self, *args, **options):
        verbosity = options.get('verbosity')
        encoding = options.get('encoding')
        filename = options.get('paths')
        structure = options.get('structure')
        name = options.get('name')
        if name:
            name = name.encode(encoding)
        srid = options.get('srid')
        do_intersect = options.get('intersect')
        comments = options.get('comments')
        if comments:
            comments = comments.encode(encoding)

        if structure or Structure.objects.count() > 1:
            try:
                structure = Structure.objects.get(name=structure)
            except Structure.DoesNotExist:
                raise CommandError("Structure does not match with instance's structures\n"
                                   "Use --structure to define it or change your option structure")
        else:
            structure = Structure.objects.first()
        if verbosity > 0:
            self.stdout.write("All paths in DataSource will be linked to the structure : %s" % structure)

        ds = DataSource(filename)

        bbox = Polygon.from_bbox(settings.SPATIAL_EXTENT)
        bbox.srid = settings.SRID
        if do_intersect:
            for layer in ds:
                for feat in layer:
                    try:
                        geom = feat.geom.geos
                        if not isinstance(geom, LineString):
                            if verbosity > 1:
                                self.stdout.write("%s's geometry is not a Linestring" % feat)
                            break
                        self.check_srid(srid, geom)
                        geom.dim = 2
                        if bbox.intersects(geom):
                            path = Path.objects.create(name=feat.get(name),
                                                       structure=structure,
                                                       geom=geom,
                                                       comments=comments)
                            if verbosity > 1:
                                self.stdout.write('Create path : {}'.format(path.name))
                    except UnicodeEncodeError:
                        self.stdout.write("Problem of encoding with %s" % feat.get(name))
        else:
            for layer in ds:
                for feat in layer:
                    try:
                        geom = feat.geom.geos
                        if not isinstance(geom, LineString):
                            if verbosity > 1:
                                self.stdout.write("%s's geometry is not a Linestring" % feat)
                            break
                        self.check_srid(srid, geom)
                        geom.dim = 2
                        if geom.within(bbox):
                            path = Path.objects.create(name=feat.get(name),
                                                       structure=structure,
                                                       geom=geom,
                                                       comments=comments)
                            if verbosity > 1:
                                self.stdout.write('Create path : {}'.format(path.pk))
                    except UnicodeEncodeError:
                        self.stdout.write("Problem of encoding with %s" % feat.get(name))

    def check_srid(self, srid, geom):
        if not geom.srid:
            geom.srid = srid
        if geom.srid != settings.SRID:
            try:
                geom.transform(settings.SRID)
            except GDALException:
                raise CommandError("SRID is not well configurate, change/add option srid")
