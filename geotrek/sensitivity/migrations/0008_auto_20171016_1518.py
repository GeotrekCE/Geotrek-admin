# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('sensitivity', '0007_species_radius'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sensitivearea',
            name='geom',
            field=django.contrib.gis.db.models.fields.GeometryField(srid=2154),
        ),
        migrations.AlterField(
            model_name='species',
            name='radius',
            field=models.IntegerField(help_text='meters', null=True, verbose_name='Bubble radius', blank=True),
        ),
    ]
