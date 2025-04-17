from django.conf import settings
from django.contrib.gis.gdal import DataSource, GDALException
from django.contrib.gis.geos.collections import MultiPolygon
from django.contrib.gis.geos.polygon import Polygon
from django.core.management.base import BaseCommand, CommandError

from geotrek.zoning.models import RestrictedArea, RestrictedAreaType


class Command(BaseCommand):
    help = "Load Restricted Area from a file within the spatial extent\n"

    def add_arguments(self, parser):
        parser.add_argument("file_path", help="File's path of the restricted area")
        parser.add_argument(
            "area_type", action="store", help="Type of restricted areas in the file"
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
            help="Check features intersect spatial extent and not only within",
        )

    def handle(self, *args, **options):
        verbosity = options.get("verbosity")
        file_path = options.get("file_path")
        area_type_name = options.get("area_type")
        name_column = options.get("name")
        encoding = options.get("encoding")
        srid = options.get("srid")
        do_intersect = options.get("intersect")
        bbox = Polygon.from_bbox(settings.SPATIAL_EXTENT)
        bbox.srid = settings.SRID
        ds = DataSource(file_path, encoding=encoding)
        count_error = 0
        area_type, created = RestrictedAreaType.objects.get_or_create(
            name=area_type_name
        )
        if verbosity > 0:
            self.stdout.write(
                f"RestrictedArea Type's {area_type_name} created"
                if created
                else f"Get {area_type_name}"
            )

        for layer in ds:
            for feat in layer:
                try:
                    geom = feat.geom.geos
                    if not isinstance(geom, Polygon) and not isinstance(
                        geom, MultiPolygon
                    ):
                        if verbosity > 0:
                            self.stdout.write(
                                f"{feat.get(name_column)}'s geometry is not a polygon"
                            )
                        break
                    elif isinstance(geom, Polygon):
                        geom = MultiPolygon(geom)
                    self.check_srid(srid, geom)
                    geom.dim = 2
                    if geom.valid:
                        if (do_intersect and bbox.intersects(geom)) or (
                            not do_intersect and geom.within(bbox)
                        ):
                            instance, created = RestrictedArea.objects.update_or_create(
                                name=feat.get(name_column),
                                area_type=area_type,
                                defaults={"geom": geom},
                            )
                            if verbosity > 0:
                                self.stdout.write(
                                    "{} {}".format(
                                        "Created" if created else "Updated",
                                        feat.get(name_column),
                                    )
                                )
                    else:
                        if verbosity > 0:
                            self.stdout.write(
                                f"{feat.get(name_column)}'s geometry is not valid"
                            )
                except IndexError:
                    if count_error == 0:
                        self.stdout.write(
                            "Name's attribute do not correspond with options\n"
                            "Please, use --name to fix it.\n"
                            "Fields in your file are : {}".format(
                                ", ".join(layer.fields)
                            )
                        )
                    count_error += 1

    def check_srid(self, srid, geom):
        if not geom.srid:
            geom.srid = int(srid)

        if geom.srid != settings.SRID:
            try:
                geom.transform(settings.SRID)
            except GDALException:
                msg = "SRID is not well configurate, change/add option srid"
                raise CommandError(msg)
