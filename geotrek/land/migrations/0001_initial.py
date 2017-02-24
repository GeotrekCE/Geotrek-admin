# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import mapentity.models
import geotrek.authent.models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0001_initial'),
        ('authent', '0001_initial'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompetenceEdge',
            fields=[
                ('topo_object', models.OneToOneField(parent_link=True, primary_key=True, db_column=b'evenement', serialize=False, to='core.Topology')),
                ('organization', models.ForeignKey(db_column=b'organisme', verbose_name='Organism', to='common.Organism')),
            ],
            options={
                'db_table': 'f_t_competence',
                'verbose_name': 'Competence edge',
                'verbose_name_plural': 'Competence edges',
            },
            bases=(mapentity.models.MapEntityMixin, 'core.topology'),
        ),
        migrations.CreateModel(
            name='LandEdge',
            fields=[
                ('topo_object', models.OneToOneField(parent_link=True, primary_key=True, db_column=b'evenement', serialize=False, to='core.Topology')),
                ('owner', models.TextField(verbose_name='Owner', db_column=b'proprietaire', blank=True)),
                ('agreement', models.BooleanField(default=False, verbose_name='Agreement', db_column=b'convention')),
            ],
            options={
                'db_table': 'f_t_foncier',
                'verbose_name': 'Land edge',
                'verbose_name_plural': 'Land edges',
            },
            bases=(mapentity.models.MapEntityMixin, 'core.topology'),
        ),
        migrations.CreateModel(
            name='LandType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128, verbose_name='Name', db_column=b'foncier')),
                ('right_of_way', models.BooleanField(default=False, verbose_name='Right of way', db_column=b'droit_de_passage')),
                ('structure', models.ForeignKey(db_column=b'structure', default=geotrek.authent.models.default_structure_pk, verbose_name='Related structure', to='authent.Structure')),
            ],
            options={
                'ordering': ['name'],
                'db_table': 'f_b_foncier',
                'verbose_name': 'Land type',
                'verbose_name_plural': 'Land types',
            },
        ),
        migrations.CreateModel(
            name='PhysicalEdge',
            fields=[
                ('topo_object', models.OneToOneField(parent_link=True, primary_key=True, db_column=b'evenement', serialize=False, to='core.Topology')),
            ],
            options={
                'db_table': 'f_t_nature',
                'verbose_name': 'Physical edge',
                'verbose_name_plural': 'Physical edges',
            },
            bases=(mapentity.models.MapEntityMixin, 'core.topology'),
        ),
        migrations.CreateModel(
            name='PhysicalType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128, verbose_name='Name', db_column=b'nom')),
                ('structure', models.ForeignKey(db_column=b'structure', default=geotrek.authent.models.default_structure_pk, verbose_name='Related structure', to='authent.Structure')),
            ],
            options={
                'ordering': ['name'],
                'db_table': 'f_b_nature',
                'verbose_name': 'Physical type',
                'verbose_name_plural': 'Physical types',
            },
        ),
        migrations.CreateModel(
            name='SignageManagementEdge',
            fields=[
                ('topo_object', models.OneToOneField(parent_link=True, primary_key=True, db_column=b'evenement', serialize=False, to='core.Topology')),
                ('organization', models.ForeignKey(db_column=b'organisme', verbose_name='Organism', to='common.Organism')),
            ],
            options={
                'db_table': 'f_t_gestion_signaletique',
                'verbose_name': 'Signage management edge',
                'verbose_name_plural': 'Signage management edges',
            },
            bases=(mapentity.models.MapEntityMixin, 'core.topology'),
        ),
        migrations.CreateModel(
            name='WorkManagementEdge',
            fields=[
                ('topo_object', models.OneToOneField(parent_link=True, primary_key=True, db_column=b'evenement', serialize=False, to='core.Topology')),
                ('organization', models.ForeignKey(db_column=b'organisme', verbose_name='Organism', to='common.Organism')),
            ],
            options={
                'db_table': 'f_t_gestion_travaux',
                'verbose_name': 'Work management edge',
                'verbose_name_plural': 'Work management edges',
            },
            bases=(mapentity.models.MapEntityMixin, 'core.topology'),
        ),
        migrations.AddField(
            model_name='physicaledge',
            name='physical_type',
            field=models.ForeignKey(db_column=b'type', verbose_name='Physical type', to='land.PhysicalType'),
        ),
        migrations.AddField(
            model_name='landedge',
            name='land_type',
            field=models.ForeignKey(db_column=b'type', verbose_name='Land type', to='land.LandType'),
        ),
    ]
