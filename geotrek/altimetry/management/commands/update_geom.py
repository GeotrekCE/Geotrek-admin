from django.core.management.base import BaseCommand, CommandError
from django.db import connection


class Command(BaseCommand):
    help = 'Reload geometries to update altimetry.\n'

    def handle(self, *args, **options):
        cur = connection.cursor()
        sql = 'SELECT * FROM raster_columns WHERE r_table_name = \'mnt\''
        cur.execute(sql)
        dem_exists = cur.rowcount != 0
        cur.close()
        if not dem_exists:
            raise CommandError("There is no DEM, the command won't do anything")
        self.stdout.write('Everything looks fine, we can start reload geometries\n')
        cur = connection.cursor()
        sql = 'SELECT update_evenement_geom_when_troncon_changes_nt();'
        cur.execute(sql)
        cur.close()
        self.stdout.write('Geometries reloaded\n')
        return
