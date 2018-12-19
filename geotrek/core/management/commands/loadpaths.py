from django.contrib.gis.gdal import DataSource, GDALException
from geotrek.core.models import Path
from geotrek.authent.models import Structure
from django.contrib.gis.geos.collections import Polygon, LineString
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db.utils import IntegrityError
from django.db import transaction


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
        parser.add_argument('--no-dry-run', '-ndr', action='store_true', dest='no_dry', default=False,
                            help="Do not change the database, dry run. Show the number of fail"
                                 " and objects potentially created")

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
        not_dry = options.get('no_dry')

        if not not_dry:
            fail = True

        counter = 0
        counter_fail = 0

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

        sid = transaction.savepoint()

        for layer in ds:
            for feat in layer:
                name = feat.get(name_column) if name_column in layer.fields else ''
                comments = feat.get(comments_column) if comments_column in layer.fields else ''
                geom = feat.geom.geos
                if not isinstance(geom, LineString):
                    if verbosity > 0:
                        self.stdout.write("%s's geometry is not a Linestring" % feat)
                    break
                self.check_srid(srid, geom)
                geom.dim = 2
                if do_intersect and bbox.intersects(geom) or not do_intersect and geom.within(bbox):
                    try:
                        with transaction.atomic():
                            path = Path.objects.create(name=name,
                                                       structure=structure,
                                                       geom=geom,
                                                       comments=comments)
                        counter += 1
                        if verbosity > 0:
                            self.stdout.write('Create path with pk : {}'.format(path.pk))
                    except IntegrityError:
                        if fail:
                            counter_fail += 1
                            self.stdout.write('Integrity Error on path : {}'.format(name))
                        else:
                            raise IntegrityError
        if not_dry:
            transaction.savepoint_commit(sid)
            if verbosity >= 2:
                self.stdout.write(self.style.NOTICE(
                    u"{0} objects created, {1} objects failed".format(counter, counter_fail)))
        else:
            transaction.savepoint_rollback(sid)
            self.stdout.write(self.style.NOTICE(
                u"{0} objects will be create, {1} objects failed;".format(counter, counter_fail)))

    def check_srid(self, srid, geom):
        if not geom.srid:
            geom.srid = srid
        if geom.srid != settings.SRID:
            try:
                geom.transform(settings.SRID)
            except GDALException:
                raise CommandError("SRID is not well configurate, change/add option srid")
