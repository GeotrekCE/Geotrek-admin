import os.path

from django.conf import settings
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import Point
from django.contrib.gis.geos.error import GEOSException
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from geotrek.authent.models import Structure
from geotrek.diving.models import Dive, Practice


class Command(BaseCommand):
    help = "Load a layer with point geometries in the Dive model\n"
    can_import_settings = True
    counter = 0

    def add_arguments(self, parser):
        parser.add_argument("point_layer")
        parser.add_argument(
            "--encoding",
            "-e",
            action="store",
            dest="encoding",
            default="utf-8",
            help="File encoding, default utf-8",
        )
        parser.add_argument("--name-field", "-n", action="store", dest="name_field")
        parser.add_argument("--depth-field", "-d", action="store", dest="depth_field")
        parser.add_argument(
            "--practice-default", action="store", dest="practice_default"
        )
        parser.add_argument(
            "--structure-default", action="store", dest="structure_default"
        )
        parser.add_argument(
            "--eid-field", action="store", dest="eid_field", help="External ID field"
        )

    def handle(self, *args, **options):
        verbosity = options.get("verbosity")

        filename = options["point_layer"]

        if not os.path.exists(filename):
            raise CommandError("File does not exists at: %s" % filename)

        data_source = DataSource(filename, encoding=options.get("encoding"))

        field_name = options.get("name_field")
        field_depth = options.get("depth_field")
        field_eid = options.get("eid_field")

        sid = transaction.savepoint()
        structure_default = options.get("structure_default")
        try:
            structure = Structure.objects.get(name=structure_default)
            if verbosity > 0:
                self.stdout.write("Dives will be linked to {}".format(structure))
        except Structure.DoesNotExist:
            self.stdout.write(
                "Structure {} set in options doesn't exist".format(structure_default)
            )
            return
        practice_default = options.get("practice_default")
        if practice_default:
            practice, created = Practice.objects.get_or_create(name=practice_default)
            if created and verbosity:
                self.stdout.write("- Practice '{}' created".format(practice))
        else:
            practice = None

        try:
            for layer in data_source:
                if verbosity >= 2:
                    self.stdout.write(
                        "- Layer '{}' with {} objects found".format(
                            layer.name, layer.num_feat
                        )
                    )
                available_fields = layer.fields
                if field_name not in available_fields:
                    self.stdout.write(
                        self.style.ERROR(
                            "Field '{}' not found in data source.".format(field_name)
                        )
                    )
                    self.stdout.write(self.style.ERROR("Set it with --name-field"))
                    break

                if field_depth and field_depth not in available_fields:
                    self.stdout.write(
                        self.style.ERROR(
                            "Field '{}' not found in data source.".format(field_depth)
                        )
                    )
                    self.stdout.write(self.style.ERROR("Set it with --depth-field"))
                    break

                if field_eid and field_eid not in available_fields:
                    self.stdout.write(
                        self.style.ERROR(
                            "Field '{}' not found in data source.".format(field_eid)
                        )
                    )
                    self.stdout.write(
                        self.style.ERROR("Change your --eid-field option")
                    )
                    break

                for feature in layer:
                    feature_geom = feature.geom.transform(settings.SRID, clone=True)
                    feature_geom.coord_dim = 2
                    name = feature.get(field_name)
                    if feature_geom.geom_type == "MultiPoint":
                        self.stdout.write(
                            self.style.NOTICE("This object is a MultiPoint : %s" % name)
                        )
                        if len(feature_geom) < 2:
                            feature_geom = feature_geom[0].geos
                        else:
                            raise CommandError(
                                "One of your geometry is a MultiPoint object with multiple points"
                            )
                    depth = (
                        feature.get(field_depth)
                        if field_depth in available_fields
                        else None
                    )
                    eid = (
                        feature.get(field_eid)
                        if field_eid in available_fields
                        else None
                    )
                    self.create_dive(
                        feature_geom, name, depth, practice, structure, verbosity, eid
                    )

            transaction.savepoint_commit(sid)
            if verbosity >= 2:
                self.stdout.write(
                    self.style.NOTICE("{} objects created.".format(self.counter))
                )

        except Exception:
            self.stdout.write(
                self.style.ERROR("An error occured, rolling back operations.")
            )
            transaction.savepoint_rollback(sid)
            raise

    def create_dive(self, geometry, name, depth, practice, structure, verbosity, eid):
        if geometry.geom_type != "Point":
            raise GEOSException("Invalid Geometry type.")
        with transaction.atomic():
            fields_without_eid = {
                "name": name,
                "depth": depth,
                "practice": practice,
                "geom": Point(geometry.x, geometry.y, srid=settings.SRID),
            }
            if eid:
                dive, created = Dive.objects.update_or_create(
                    eid=eid, defaults=fields_without_eid
                )
                if verbosity > 0 and not created:
                    self.stdout.write("Update : %s with eid %s" % (name, eid))
            else:
                dive = Dive.objects.create(**fields_without_eid)
        self.counter += 1

        return dive
