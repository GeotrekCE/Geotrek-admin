from django.contrib.gis.gdal import DataSource, GDALException
from geotrek.core.models import Path
from geotrek.authent.models import Structure
from django.contrib.gis.geos.collections import Polygon, LineString
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db.utils import IntegrityError


class Command(BaseCommand):
    help = 'Load Paths from a file within the spatial extent\n'

    def add_arguments(self, parser):
        parser.add_argument('file_path', help="File's path of the paths")
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
        parser.add_argument('--fail', '-f', action='store_true', dest='fail', default=False,
                            help="Allows to grant fails")

    def handle(self, *args, **options):
        verbosity = options.get('verbosity')
        encoding = options.get('encoding')
        file_path = options.get('file_path')
        structure = options.get('structure')
        name_column = options.get('name')
        srid = options.get('srid')
        do_intersect = options.get('intersect')
        comments_column = options.get('comments')
        fail = options.get('fail')

        if structure:
            try:
                structure = Structure.objects.get(name=structure)
            except Structure.DoesNotExist:
                raise CommandError("Structure does not match with instance's structures\n"
                                   "Change your option --structure")
        elif Structure.objects.count() == 1:
            structure = Structure.objects.first()
        else:
            raise CommandError("There are more than 1 structure and you didn't define the option structure\n"
                               "Use --structure to define it")
        if verbosity > 0:
            self.stdout.write("All paths in DataSource will be linked to the structure : %s" % structure)

        ds = DataSource(file_path, encoding=encoding)

        bbox = Polygon.from_bbox(settings.SPATIAL_EXTENT)
        bbox.srid = settings.SRID

        for layer in ds:
            for feat in layer:
                name = feat.get(name_column) if name_column in layer.fields else ''
                comments = feat.get(comments_column) if comments_column in layer.fields else ''
                try:
                    geom = feat.geom.geos
                    if not isinstance(geom, LineString):
                        if verbosity > 0:
                            self.stdout.write("%s's geometry is not a Linestring" % feat)
                        break
                    self.check_srid(srid, geom)
                    geom.dim = 2
                    if do_intersect and bbox.intersects(geom) or not do_intersect and geom.within(bbox):
                        try:
                            path = Path.objects.create(name=name,
                                                       structure=structure,
                                                       geom=geom,
                                                       comments=comments)
                            if verbosity > 0:
                                self.stdout.write('Create path with pk : {}'.format(path.pk))
                        except IntegrityError:
                            if fail:
                                self.stdout.write('Integrity Error on path : {}'.format(name))
                            else:
                                raise IntegrityError
                except UnicodeEncodeError:
                    self.stdout.write("Problem of encoding with %s" % name)

    def check_srid(self, srid, geom):
        if not geom.srid:
            geom.srid = srid
        if geom.srid != settings.SRID:
            try:
                geom.transform(settings.SRID)
            except GDALException:
                raise CommandError("SRID is not well configurate, change/add option srid")
