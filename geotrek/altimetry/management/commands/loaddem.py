import os.path
import tempfile
from subprocess import PIPE, call

from django.apps import apps
from django.conf import settings
from django.contrib.gis.gdal import GDALRaster
from django.contrib.gis.gdal.error import GDALException
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.db.models import F

from geotrek.altimetry.models import AltimetryMixin, Dem
from geotrek.core.models import Topology


class Command(BaseCommand):
    help = "Load DEM data (projecting and clipping it if necessary).\n"
    help += "You may need to create a GDAL Virtual Raster if your DEM is "
    help += "composed of several files.\n"
    can_import_settings = True

    def add_arguments(self, parser):
        parser.add_argument("dem_path")
        parser.add_argument(
            "--replace",
            action="store_true",
            default=False,
            help="Replace existing DEM if any.",
        )
        parser.add_argument(
            "--update-altimetry",
            action="store_true",
            default=False,
            help="Update altimetry of all 3D geometries, /!\\ This option takes lot of time to perform",
        )

    def handle(self, *args, **options):
        verbose = options["verbosity"] != 0

        update_altimetry_paths = options["update_altimetry"]

        try:
            cmd = "raster2pgsql -G > /dev/null"
            kwargs_raster = {"shell": True}
            ret = self.call_command_system(cmd, **kwargs_raster)
            if ret != 0:
                msg = f"raster2pgsql failed with exit code {ret}"
                raise Exception(msg)
        except Exception as e:
            msg = f"Caught {e.__class__.__name__}: {e}"
            raise CommandError(msg)
        if verbose:
            self.stdout.write("-- Checking input DEM ------------------\n")
        # Obtain DEM path
        dem_path = options["dem_path"]

        # Open GDAL dataset
        if not os.path.exists(dem_path):
            msg = f"DEM file does not exists at: {dem_path}"
            raise CommandError(msg)
        try:
            rst = GDALRaster(dem_path, write=False)
        except GDALException:
            msg = "DEM format is not recognized by GDAL."
            raise CommandError(msg)

        # GDAL dataset check 1: ensure dataset has a known SRS
        if not rst.srs:
            msg = "DEM coordinate system is unknown."
            raise CommandError(msg)
        # Obtain dataset SRS
        if settings.SRID != rst.srs.srid:
            rst = rst.transform(settings.SRID)

        dem_exists = Dem.objects.exists()

        # Obtain replace mode
        replace = options["replace"]

        # What to do with existing DEM (if any)
        if dem_exists and replace:
            # Drop table content
            Dem.objects.all().delete()
        elif dem_exists and not replace:
            msg = "DEM file exists, use --replace to overwrite"
            raise CommandError(msg)

        if verbose:
            self.stdout.write("Everything looks fine, we can start loading DEM\n")

        output = tempfile.NamedTemporaryFile()  # SQL code for raster creation
        cmd = "raster2pgsql -a -M -t 100x100 {} altimetry_dem {}".format(
            rst.name,
            "" if verbose else "2>/dev/null",
        )
        try:
            if verbose:
                self.stdout.write("\n-- Relaying to raster2pgsql ------------\n")
                self.stdout.write(cmd)
            kwargs_raster2 = {"shell": True, "stdout": output.file, "stderr": PIPE}
            ret = self.call_command_system(cmd, **kwargs_raster2)
            if ret != 0:
                msg = f"raster2pgsql failed with exit code {ret}"
                raise Exception(msg)
        except Exception as e:
            output.close()
            msg = f"Caught {e.__class__.__name__}: {e}"
            raise CommandError(msg)

        if verbose:
            self.stdout.write("DEM successfully converted to SQL.\n")

        # Step 3: Dump SQL code into database
        if verbose:
            self.stdout.write("\n-- Loading DEM into database -----------\n")
        with connection.cursor() as cur:
            output.file.seek(0)
            for sql_line in output.file:
                cur.execute(sql_line)

        output.close()
        if verbose:
            self.stdout.write("DEM successfully loaded.\n")
        if update_altimetry_paths:
            if verbose:
                self.stdout.write("Updating 3d geometries.\n")
            for model in apps.get_models():
                if "geom" in [
                    field.name for field in model._meta.get_fields()
                ] and issubclass(model, AltimetryMixin):
                    if settings.TREKKING_TOPOLOGY_ENABLED:
                        if not issubclass(model, Topology):
                            model.objects.all().update(geom=F("geom"))
                    else:
                        model.objects.all().update(geom=F("geom"))
        return

    def call_command_system(self, cmd, **kwargs):
        return_code = call(cmd, **kwargs)
        return return_code
