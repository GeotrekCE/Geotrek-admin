# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import mapentity.models
import django.contrib.gis.db.models.fields
import django.db.models.deletion
import geotrek.common.mixins
import geotrek.authent.models


class Migration(migrations.Migration):

    dependencies = [
        ('authent', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comfort',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comfort', models.CharField(max_length=50, verbose_name='Comfort', db_column=b'confort')),
                ('structure', models.ForeignKey(db_column=b'structure', default=geotrek.authent.models.default_structure_pk, verbose_name='Related structure', to='authent.Structure')),
            ],
            options={
                'ordering': ['comfort'],
                'db_table': 'l_b_confort',
                'verbose_name': 'Comfort',
                'verbose_name_plural': 'Comforts',
            },
        ),
        migrations.CreateModel(
            name='Network',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('network', models.CharField(max_length=50, verbose_name='Network', db_column=b'reseau')),
                ('structure', models.ForeignKey(db_column=b'structure', default=geotrek.authent.models.default_structure_pk, verbose_name='Related structure', to='authent.Structure')),
            ],
            options={
                'ordering': ['network'],
                'db_table': 'l_b_reseau',
                'verbose_name': 'Network',
                'verbose_name_plural': 'Networks',
            },
        ),
        migrations.CreateModel(
            name='Path',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_insert', models.DateTimeField(auto_now_add=True, verbose_name='Insertion date', db_column=b'date_insert')),
                ('date_update', models.DateTimeField(auto_now=True, verbose_name='Update date', db_column=b'date_update')),
                ('geom_3d', django.contrib.gis.db.models.fields.GeometryField(dim=3, default=None, editable=False, srid=settings.SRID, null=True, spatial_index=False)),
                ('length', models.FloatField(db_column=b'longueur', default=0.0, editable=False, blank=True, null=True, verbose_name='3D Length')),
                ('ascent', models.IntegerField(db_column=b'denivelee_positive', default=0, editable=False, blank=True, null=True, verbose_name='Ascent')),
                ('descent', models.IntegerField(db_column=b'denivelee_negative', default=0, editable=False, blank=True, null=True, verbose_name='Descent')),
                ('min_elevation', models.IntegerField(db_column=b'altitude_minimum', default=0, editable=False, blank=True, null=True, verbose_name='Minimum elevation')),
                ('max_elevation', models.IntegerField(db_column=b'altitude_maximum', default=0, editable=False, blank=True, null=True, verbose_name='Maximum elevation')),
                ('slope', models.FloatField(db_column=b'pente', default=0.0, editable=False, blank=True, null=True, verbose_name='Slope')),
                ('geom', django.contrib.gis.db.models.fields.LineStringField(srid=settings.SRID, spatial_index=False)),
                ('geom_cadastre', django.contrib.gis.db.models.fields.LineStringField(srid=settings.SRID, spatial_index=False, null=True, editable=False)),
                ('valid', models.BooleanField(default=True, help_text='Approved by manager', verbose_name='Validity', db_column=b'valide')),
                ('visible', models.BooleanField(default=True, help_text='Shown in lists and maps', verbose_name='Visible', db_column=b'visible')),
                ('name', models.CharField(db_column=b'nom', max_length=20, blank=True, help_text='Official name', null=True, verbose_name='Name')),
                ('comments', models.TextField(help_text='Remarks', null=True, verbose_name='Comments', db_column=b'remarques', blank=True)),
                ('departure', models.CharField(db_column=b'depart', default=b'', max_length=250, blank=True, help_text='Departure place', null=True, verbose_name='Departure')),
                ('arrival', models.CharField(db_column=b'arrivee', default=b'', max_length=250, blank=True, help_text='Arrival place', null=True, verbose_name='Arrival')),
                ('eid', models.CharField(max_length=128, null=True, verbose_name='External id', db_column=b'id_externe', blank=True)),
                ('comfort', models.ForeignKey(related_name='paths', db_column=b'confort', blank=True, to='core.Comfort', null=True, verbose_name='Comfort')),
                ('networks', models.ManyToManyField(related_name='paths', db_table=b'l_r_troncon_reseau', verbose_name='Networks', to='core.Network', blank=True)),
            ],
            options={
                'db_table': 'l_t_troncon',
                'verbose_name': 'Path',
                'verbose_name_plural': 'Paths',
            },
            bases=(geotrek.common.mixins.AddPropertyMixin, mapentity.models.MapEntityMixin, models.Model),
        ),
        migrations.CreateModel(
            name='PathAggregation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_position', models.FloatField(verbose_name='Start position', db_column=b'pk_debut', db_index=True)),
                ('end_position', models.FloatField(verbose_name='End position', db_column=b'pk_fin', db_index=True)),
                ('order', models.IntegerField(default=0, null=True, verbose_name='Order', db_column=b'ordre', blank=True)),
                ('path', models.ForeignKey(related_name='aggregations', on_delete=django.db.models.deletion.DO_NOTHING, db_column=b'troncon', verbose_name='Path', to='core.Path')),
            ],
            options={
                'ordering': ['order'],
                'db_table': 'e_r_evenement_troncon',
                'verbose_name': 'Path aggregation',
                'verbose_name_plural': 'Path aggregations',
            },
        ),
        migrations.CreateModel(
            name='PathSource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('source', models.CharField(max_length=50, verbose_name='Source')),
                ('structure', models.ForeignKey(db_column=b'structure', default=geotrek.authent.models.default_structure_pk, verbose_name='Related structure', to='authent.Structure')),
            ],
            options={
                'ordering': ['source'],
                'db_table': 'l_b_source_troncon',
                'verbose_name': 'Path source',
                'verbose_name_plural': 'Path sources',
            },
        ),
        migrations.CreateModel(
            name='Stake',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('stake', models.CharField(max_length=50, verbose_name='Stake', db_column=b'enjeu')),
                ('structure', models.ForeignKey(db_column=b'structure', default=geotrek.authent.models.default_structure_pk, verbose_name='Related structure', to='authent.Structure')),
            ],
            options={
                'ordering': ['id'],
                'db_table': 'l_b_enjeu',
                'verbose_name': 'Maintenance stake',
                'verbose_name_plural': 'Maintenance stakes',
            },
        ),
        migrations.CreateModel(
            name='Topology',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_insert', models.DateTimeField(auto_now_add=True, verbose_name='Insertion date', db_column=b'date_insert')),
                ('date_update', models.DateTimeField(auto_now=True, verbose_name='Update date', db_column=b'date_update')),
                ('deleted', models.BooleanField(default=False, verbose_name='Deleted', editable=False, db_column=b'supprime')),
                ('geom_3d', django.contrib.gis.db.models.fields.GeometryField(dim=3, default=None, editable=False, srid=settings.SRID, null=True, spatial_index=False)),
                ('length', models.FloatField(db_column=b'longueur', default=0.0, editable=False, blank=True, null=True, verbose_name='3D Length')),
                ('ascent', models.IntegerField(db_column=b'denivelee_positive', default=0, editable=False, blank=True, null=True, verbose_name='Ascent')),
                ('descent', models.IntegerField(db_column=b'denivelee_negative', default=0, editable=False, blank=True, null=True, verbose_name='Descent')),
                ('min_elevation', models.IntegerField(db_column=b'altitude_minimum', default=0, editable=False, blank=True, null=True, verbose_name='Minimum elevation')),
                ('max_elevation', models.IntegerField(db_column=b'altitude_maximum', default=0, editable=False, blank=True, null=True, verbose_name='Maximum elevation')),
                ('slope', models.FloatField(db_column=b'pente', default=0.0, editable=False, blank=True, null=True, verbose_name='Slope')),
                ('offset', models.FloatField(default=0.0, verbose_name='Offset', db_column=b'decallage')),
                ('kind', models.CharField(verbose_name='Kind', max_length=32, editable=False)),
                ('geom', django.contrib.gis.db.models.fields.GeometryField(default=None, srid=settings.SRID, spatial_index=False, null=True, editable=False)),
            ],
            options={
                'db_table': 'e_t_evenement',
                'verbose_name': 'Topology',
                'verbose_name_plural': 'Topologies',
            },
            bases=(geotrek.common.mixins.AddPropertyMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Usage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('usage', models.CharField(max_length=50, verbose_name='Usage', db_column=b'usage')),
                ('structure', models.ForeignKey(db_column=b'structure', default=geotrek.authent.models.default_structure_pk, verbose_name='Related structure', to='authent.Structure')),
            ],
            options={
                'ordering': ['usage'],
                'db_table': 'l_b_usage',
                'verbose_name': 'Usage',
                'verbose_name_plural': 'Usages',
            },
        ),
        migrations.CreateModel(
            name='Trail',
            fields=[
                ('topo_object', models.OneToOneField(parent_link=True, primary_key=True, db_column=b'evenement', serialize=False, to='core.Topology')),
                ('name', models.CharField(max_length=64, verbose_name='Name', db_column=b'nom')),
                ('departure', models.CharField(max_length=64, verbose_name='Departure', db_column=b'depart')),
                ('arrival', models.CharField(max_length=64, verbose_name='Arrival', db_column=b'arrivee')),
                ('comments', models.TextField(default=b'', verbose_name='Comments', db_column=b'commentaire', blank=True)),
                ('structure', models.ForeignKey(db_column=b'structure', default=geotrek.authent.models.default_structure_pk, verbose_name='Related structure', to='authent.Structure')),
            ],
            options={
                'ordering': ['name'],
                'db_table': 'l_t_sentier',
                'verbose_name': 'Trail',
                'verbose_name_plural': 'Trails',
            },
            bases=(mapentity.models.MapEntityMixin, 'core.topology', models.Model),
        ),
        migrations.AddField(
            model_name='topology',
            name='paths',
            field=models.ManyToManyField(to='core.Path', through='core.PathAggregation', verbose_name='Path', db_column=b'troncons'),
        ),
        migrations.AddField(
            model_name='pathaggregation',
            name='topo_object',
            field=models.ForeignKey(related_name='aggregations', db_column=b'evenement', verbose_name='Topology', to='core.Topology'),
        ),
        migrations.AddField(
            model_name='path',
            name='source',
            field=models.ForeignKey(related_name='paths', db_column=b'source', blank=True, to='core.PathSource', null=True, verbose_name='Source'),
        ),
        migrations.AddField(
            model_name='path',
            name='stake',
            field=models.ForeignKey(related_name='paths', db_column=b'enjeu', blank=True, to='core.Stake', null=True, verbose_name='Maintenance stake'),
        ),
        migrations.AddField(
            model_name='path',
            name='structure',
            field=models.ForeignKey(db_column=b'structure', default=geotrek.authent.models.default_structure_pk, verbose_name='Related structure', to='authent.Structure'),
        ),
        migrations.AddField(
            model_name='path',
            name='usages',
            field=models.ManyToManyField(related_name='paths', db_table=b'l_r_troncon_usage', verbose_name='Usages', to='core.Usage', blank=True),
        ),
    ]
