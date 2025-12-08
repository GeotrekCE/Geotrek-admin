from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("zoning", "0005_auto_20201126_0706"),
    ]

    operations = [
        # 10_zoning
        migrations.RunSQL("DROP INDEX IF EXISTS couche_communes_geom_idx;"),
        migrations.RunSQL("DROP INDEX IF EXISTS l_commune_geom_idx;"),
        migrations.RunSQL("DROP INDEX IF EXISTS zoning_city_geom_idx;"),
        migrations.RunSQL("DROP INDEX IF EXISTS couche_secteurs_geom_idx;"),
        migrations.RunSQL("DROP INDEX IF EXISTS l_secteur_geom_idx;"),
        migrations.RunSQL("DROP INDEX IF EXISTS zoning_district_geom_idx;"),
        migrations.RunSQL("DROP INDEX IF EXISTS couche_zonage_reglementaire_geom_idx;"),
        migrations.RunSQL("DROP INDEX IF EXISTS l_zonage_reglementaire_geom_idx;"),
        migrations.RunSQL("DROP INDEX IF EXISTS zoning_restrictedarea_geom_idx;"),
    ]
