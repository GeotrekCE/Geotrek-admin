# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CirkwiLocomotion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('eid', models.IntegerField(unique=True, verbose_name='Cirkwi id')),
                ('name', models.CharField(max_length=128, verbose_name='Cirkwi name', db_column=b'nom')),
            ],
            options={
                'ordering': ['name'],
                'db_table': 'o_b_cirkwi_locomotion',
                'verbose_name': 'Cirkwi locomotion',
                'verbose_name_plural': 'Cirkwi locomotions',
            },
        ),
        migrations.CreateModel(
            name='CirkwiPOICategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('eid', models.IntegerField(unique=True, verbose_name='Cirkwi id')),
                ('name', models.CharField(max_length=128, verbose_name='Cirkwi name', db_column=b'nom')),
            ],
            options={
                'ordering': ['name'],
                'db_table': 'o_b_cirkwi_poi_category',
                'verbose_name': 'Cirkwi POI category',
                'verbose_name_plural': 'Cirkwi POI categories',
            },
        ),
        migrations.CreateModel(
            name='CirkwiTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('eid', models.IntegerField(unique=True, verbose_name='Cirkwi id')),
                ('name', models.CharField(max_length=128, verbose_name='Cirkwi name', db_column=b'nom')),
            ],
            options={
                'ordering': ['name'],
                'db_table': 'o_b_cirkwi_tag',
                'verbose_name': 'Cirkwi tag',
                'verbose_name_plural': 'Cirkwi tags',
            },
        ),
    ]
