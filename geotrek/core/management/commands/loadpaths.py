from django.conf import settings
from django.contrib.gis.gdal import DataSource, GDALException
from django.contrib.gis.geos.collections import LineString, Polygon
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.utils import IntegrityError, InternalError

from geotrek.authent.models import Structure
from geotrek.core.models import Path


class Command(BaseCommand):
    help = "Load Paths from a file within the spatial extent\n"

    def add_arguments(self, parser):
        parser.add_argument("file_path", help="File's path of the paths")
        parser.add_argument(
            "--structure", action="store", dest="structure", help="Define the structure"
        )
        parser.add_argument(
            "--name-attribute",
            "-n",
            action="store",
            dest="name",
            default="nom",
            help="Name of the name's attribute inside the file",
        )
        parser.add_argument(
            "--comments-attribute",
            "-c",
            nargs="*",
            action="store",
            dest="comment",
            help="",
        )
        parser.add_argument(
            "--encoding",
            "-e",
            action="store",
            dest="encoding",
            default="utf-8",
            help="File encoding, default utf-8",
        )
        parser.add_argument(
            "--srid",
            "-s",
            action="store",
            dest="srid",
            default=4326,
            type=int,
            help="File's SRID",
        )
        parser.add_argument(
            "--intersect",
            "-i",
            action="store_true",
            dest="intersect",
            default=False,
            help="Check paths intersect spatial extent and not only within",
        )
        parser.add_argument(
            "--fail",
            "-f",
            action="store_true",
            dest="fail",
            default=False,
            help="Allows to grant fails",
        )
        parser.add_argument(
            "--dry",
            "-d",
            action="store_true",
            dest="dry",
            default=False,
            help="Do not change the database, dry run. Show the number of fail"
            " and objects potentially created",
        )

    def handle(self, *args, **options):
        verbosity = options.get("verbosity")
        encoding = options.get("encoding")
        file_path = options.get("file_path")
        structure = options.get("structure")
        name_column = options.get("name")
        srid = options.get("srid")
        self.do_intersect = options.get("intersect")
        comments_columns = options.get("comment")
        fail = options.get("fail")
        dry = options.get("dry")

        if dry:
            fail = True

        counter = 0
        counter_fail = 0

        if structure:
            try:
                structure = Structure.objects.get(name=structure)
            except Structure.DoesNotExist:
                raise CommandError(
                    "Structure does not match with instance's structures\n"
                    "Change your option --structure"
                )
        elif Structure.objects.count() == 1:
            structure = Structure.objects.first()
        else:
            raise CommandError(
                "There are more than 1 structure and you didn't define the option structure\n"
                "Use --structure to define it"
            )
        if verbosity > 0:
            self.stdout.write(
                "All paths in DataSource will be linked to the structure : %s"
                % structure
            )

        ds = DataSource(file_path, encoding=encoding)

        self.bbox = Polygon.from_bbox(settings.SPATIAL_EXTENT)
        self.bbox.srid = settings.SRID

        sid = transaction.savepoint()

        for layer in ds:
            for feat in layer:
                name = feat.get(name_column) if name_column in layer.fields else ""
                comment_final_tab = []
                if comments_columns:
                    for comment_column in comments_columns:
                        if comment_column in layer.fields:
                            comment_final_tab.append(feat.get(comment_column))
                geom = feat.geom.geos
                if not isinstance(geom, LineString):
                    if verbosity > 0:
                        self.stdout.write("%s's geometry is not a Linestring" % feat)
                    break
                self.check_srid(srid, geom)
                geom.dim = 2
                if self.should_import(feat, geom):
                    try:
                        with transaction.atomic():
                            comment_final = "</br>".join(comment_final_tab)
                            path = Path.objects.create(
                                name=name,
                                structure=structure,
                                geom=geom,
                                comments=comment_final,
                            )
                        counter += 1
                        if verbosity > 0:
                            self.stdout.write(
                                f"Create path with pk : {path.pk}"
                            )
                        if verbosity > 1:
                            self.stdout.write(
                                "The comment %s was added on %s" % (comment_final, name)
                            )
                    except (IntegrityError, InternalError):
                        if fail:
                            counter_fail += 1
                            self.stdout.write(
                                f"Integrity Error on path : {name}, {geom}"
                            )
                        else:
                            raise
        if not dry:
            transaction.savepoint_commit(sid)
            if verbosity >= 2:
                self.stdout.write(
                    self.style.NOTICE(
                        f"{counter} objects created, {counter_fail} objects failed"
                    )
                )
        else:
            transaction.savepoint_rollback(sid)
            self.stdout.write(
                self.style.NOTICE(
                    f"{counter} objects will be create, {counter_fail} objects failed;"
                )
            )

    def check_srid(self, srid, geom):
        if not geom.srid:
            geom.srid = srid
        if geom.srid != settings.SRID:
            try:
                geom.transform(settings.SRID)
            except GDALException:
                raise CommandError(
                    "SRID is not well configurate, change/add option srid"
                )

    def should_import(self, feature, geom):
        return (
            self.do_intersect
            and self.bbox.intersects(geom)
            or not self.do_intersect
            and geom.within(self.bbox)
        )
