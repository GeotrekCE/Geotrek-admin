from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.conf import settings
from optparse import make_option
import os.path
from subprocess import call
import tempfile


class Command(BaseCommand):
    args = '<dem_path>'
    help = 'Load DEM data (projecting and clipping it if necessary).\n'
    help += 'You may need to create a GDAL Virtual Raster if your DEM is '
    help += 'composed of several files.\n'
    can_import_settings = True

    option_list = BaseCommand.option_list + (
        make_option('--replace',
                    action='store_true',
                    default=False,
                    help='Replace existing DEM if any.'),
    )

    def handle(self, *args, **options):

        try:
            from osgeo import gdal, ogr, osr
        except ImportError:
            msg = 'GDAL Python bindings are not available. Can not proceed.'
            raise CommandError(msg)

        try:
            ret = call('raster2pgsql -G', shell=True)
            if ret != 0:
                raise Exception('raster2pgsql failed with exit code %d' % ret)
        except Exception as e:
            msg = 'Caught %s: %s' % (e.__class__.__name__, e,)
            raise CommandError(msg)

        self.stdout.write('-- Checking input DEM ------------------\n')

        # Validate arguments
        if len(args) != 1:
            self.stdout.write(self.usage('loaddem'))
            return

        # Obtain DEM path
        dem_path = args[0]

        # Open GDAL dataset
        if not os.path.exists(dem_path):
            raise CommandError('DEM file does not exists at: %s' % dem_path)
        ds = gdal.Open(dem_path)
        if ds is None:
            raise CommandError('DEM format is not recognized by GDAL.')

        # GDAL dataset check 1: ensure dataset has a known SRS
        if ds.GetProjection() == '':
            raise CommandError('DEM coordinate system is unknown.')

        wkt_box = 'POLYGON(({0} {1}, {2} {1}, {2} {3}, {0} {3}, {0} {1}))'

        # Obtain dataset SRS
        srs_r = osr.SpatialReference()
        srs_r.ImportFromWkt(ds.GetProjection())

        # Obtain project SRS
        srs_p = osr.SpatialReference()
        srs_p.ImportFromEPSG(settings.SRID)

        # Obtain dataset BBOX
        gt = ds.GetGeoTransform()
        if gt is None:
            raise CommandError('DEM extent is unknown.')
        xsize = ds.RasterXSize
        ysize = ds.RasterYSize
        minx = gt[0]
        miny = gt[3] + ysize * gt[5]
        maxx = gt[0] + xsize * gt[1]
        maxy = gt[3]
        bbox_wkt = wkt_box.format(minx, miny, maxx, maxy)
        bbox_r = ogr.CreateGeometryFromWkt(bbox_wkt, srs_r)
        bbox_r.TransformTo(srs_p)

        # Obtain project BBOX
        bbox_wkt = wkt_box.format(*settings.SPATIAL_EXTENT)
        bbox_p = ogr.CreateGeometryFromWkt(bbox_wkt, srs_p)

        # GDAL dataset check 2: ensure dataset bbox matches project extent
        if not bbox_p.Intersects(bbox_r):
            raise CommandError('DEM file does not match project extent (%s <> %s).' % (bbox_r, bbox_p))

        # Allow GDAL objects to be garbage-collected
        ds = None
        srs_p = None
        srs_r = None
        bbox_r = None
        bbox_p = None

        # Check if DEM table already exists
        cur = connection.cursor()
        sql = 'SELECT * FROM raster_columns WHERE r_table_name = \'mnt\''
        cur.execute(sql)
        dem_exists = cur.rowcount != 0
        cur.close()

        # Obtain replace mode
        replace = options['replace']

        # What to do with existing DEM (if any)
        if dem_exists and replace:
            # Drop table
            cur = connection.cursor()
            sql = 'DROP TABLE mnt'
            cur.execute(sql)
            cur.close()
        elif dem_exists and not replace:
            raise CommandError('DEM file exists, use --replace to overwrite')

        self.stdout.write('Everything looks fine, we can start loading DEM\n')

        # Unfortunately, PostGISRaster driver in GDAL does not have write mode
        # so far. Therefore, we relay parameters to standard commands using
        # subprocesses.

        # Step 1: process raster (clip, project)
        new_dem = tempfile.NamedTemporaryFile()
        cmd = 'gdalwarp -t_srs EPSG:%d -te %f %f %f %f %s %s' % (settings.SRID,
                                                                 settings.SPATIAL_EXTENT[0],
                                                                 settings.SPATIAL_EXTENT[1],
                                                                 settings.SPATIAL_EXTENT[2],
                                                                 settings.SPATIAL_EXTENT[3],
                                                                 dem_path,
                                                                 new_dem.name)
        try:
            self.stdout.write('\n-- Relaying to gdalwarp ----------------\n')
            self.stdout.write(cmd)
            ret = call(cmd, shell=True)
            if ret != 0:
                raise Exception('gdalwarp failed with exit code %d' % ret)
        except Exception as e:
            new_dem.close()
            msg = 'Caught %s: %s' % (e.__class__.__name__, e,)
            raise CommandError(msg)
        self.stdout.write('DEM successfully clipped/projected.\n')

        # Step 2: Convert to PostGISRaster format
        output = tempfile.NamedTemporaryFile()  # SQL code for raster creation
        cmd = 'raster2pgsql -c -C -I -M -t 100x100 %s mnt' % new_dem.name
        try:
            self.stdout.write('\n-- Relaying to raster2pgsql ------------\n')
            self.stdout.write(cmd)
            ret = call(cmd, stdout=output.file, shell=True)
            if ret != 0:
                raise Exception('raster2pgsql failed with exit code %d' % ret)
        except Exception as e:
            output.close()
            msg = 'Caught %s: %s' % (e.__class__.__name__, e,)
            raise CommandError(msg)
        finally:
            new_dem.close()
        self.stdout.write('DEM successfully converted to SQL.\n')

        # Step 3: Dump SQL code into database
        self.stdout.write('\n-- Loading DEM into database -----------\n')
        cur = connection.cursor()
        output.file.seek(0)
        for sql_line in output.file:
            cur.execute(sql_line)
        cur.close()
        output.close()
        self.stdout.write('DEM successfully loaded.\n')
        return
