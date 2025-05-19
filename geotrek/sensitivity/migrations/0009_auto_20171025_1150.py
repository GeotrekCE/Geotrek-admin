import django.contrib.gis.db.models.fields
from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("sensitivity", "0008_auto_20171017_1533"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sensitivearea",
            name="geom",
            field=django.contrib.gis.db.models.fields.GeometryField(srid=settings.SRID),
        ),
    ]
