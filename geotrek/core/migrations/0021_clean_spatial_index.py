from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0020_auto_20210121_0943"),
    ]

    operations = [
        # 20_path
        migrations.RunSQL("DROP INDEX IF EXISTS evenements_geom_idx;"),
        migrations.RunSQL("DROP INDEX IF EXISTS e_t_evenement_geom_idx;"),
        migrations.RunSQL("DROP INDEX IF EXISTS core_topology_geom_idx;"),
        # 40_path
        migrations.RunSQL("DROP INDEX IF EXISTS troncons_geom_idx;"),
        migrations.RunSQL("DROP INDEX IF EXISTS l_t_troncon_geom_idx;"),
        migrations.RunSQL("DROP INDEX IF EXISTS core_path_geom_idx;"),
        migrations.RunSQL("DROP INDEX IF EXISTS troncons_geom_cadastre_idx;"),
        migrations.RunSQL("DROP INDEX IF EXISTS l_t_troncon_geom_cadastre_idx;"),
        migrations.RunSQL("DROP INDEX IF EXISTS troncons_geom_cadastre_idx;"),
        migrations.RunSQL("DROP INDEX IF EXISTS l_t_troncon_geom_3d_idx;"),
        migrations.RunSQL("DROP INDEX IF EXISTS core_path_geom_3d_idx;"),
        migrations.RunSQL("DROP INDEX IF EXISTS core_path_geom_cadastre_idx;"),
        migrations.RunSQL("DROP INDEX IF EXISTS troncons_start_point_idx;"),
        migrations.RunSQL("DROP INDEX IF EXISTS l_t_troncon_start_point_idx;"),
        migrations.RunSQL("DROP INDEX IF EXISTS core_path_start_point_idx;"),
        migrations.RunSQL("DROP INDEX IF EXISTS troncons_end_point_idx;"),
        migrations.RunSQL("DROP INDEX IF EXISTS l_t_troncon_end_point_idx;"),
        migrations.RunSQL("DROP INDEX IF EXISTS core_path_end_point_idx;"),
    ]
