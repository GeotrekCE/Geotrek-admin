# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import geotrek.authent.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Structure',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256, verbose_name='Nom')),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Structure',
                'verbose_name_plural': 'Structures',
                'permissions': (('can_bypass_structure', 'Can bypass structure'),),
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(default=b'fr', max_length=10, verbose_name='Language', choices=[(b'en', b'English'), (b'fr', b'French'), (b'it', b'Italian'), (b'es', b'Spanish')])),
                ('structure', models.ForeignKey(db_column=b'structure', default=geotrek.authent.models.default_structure_pk, verbose_name='Related structure', to='authent.Structure')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': "User's profile",
                'verbose_name_plural': "User's profiles",
            },
        ),
    ]
