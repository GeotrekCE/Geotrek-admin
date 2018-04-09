# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('sensitivity', '0008_auto_20171017_1533'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sensitivearea',
            name='geom',
            field=django.contrib.gis.db.models.fields.GeometryField(srid=settings.SRID),
        ),
    ]
