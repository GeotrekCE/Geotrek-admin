from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("sensitivity", "0012_auto_20171108_1715"),
    ]

    operations = [
        migrations.AlterModelTable(
            name="species",
            table="s_b_espece_ou_suite_zone_regl",
        ),
    ]
