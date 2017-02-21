# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import mapentity.models
import django.contrib.gis.db.models.fields
import geotrek.common.mixins
import django.core.validators
import geotrek.authent.models


class Migration(migrations.Migration):

    dependencies = [
        ('tourism', '0001_initial'),
        ('common', '0001_initial'),
        ('authent', '0001_initial'),
        ('cirkwi', '0001_initial'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Accessibility',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pictogram', models.FileField(db_column=b'picto', upload_to=b'upload', max_length=512, blank=True, null=True, verbose_name='Pictogram')),
                ('name', models.CharField(max_length=128, verbose_name='Name', db_column=b'nom')),
                ('cirkwi', models.ForeignKey(verbose_name='Cirkwi tag', blank=True, to='cirkwi.CirkwiTag', null=True)),
            ],
            options={
                'ordering': ['name'],
                'db_table': 'o_b_accessibilite',
                'verbose_name': 'Accessibility',
                'verbose_name_plural': 'Accessibilities',
            },
        ),
        migrations.CreateModel(
            name='DifficultyLevel',
            fields=[
                ('pictogram', models.FileField(db_column=b'picto', upload_to=b'upload', max_length=512, blank=True, null=True, verbose_name='Pictogram')),
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('difficulty', models.CharField(max_length=128, verbose_name='Difficulty level', db_column=b'difficulte')),
                ('cirkwi_level', models.IntegerField(help_text='Between 1 and 8', null=True, verbose_name='Cirkwi level', db_column=b'niveau_cirkwi', blank=True)),
                ('cirkwi', models.ForeignKey(verbose_name='Cirkwi tag', blank=True, to='cirkwi.CirkwiTag', null=True)),
            ],
            options={
                'ordering': ['id'],
                'db_table': 'o_b_difficulte',
                'verbose_name': 'Difficulty level',
                'verbose_name_plural': 'Difficulty levels',
            },
        ),
        migrations.CreateModel(
            name='OrderedTrekChild',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField(default=0)),
            ],
            options={
                'ordering': ('parent__id', 'order'),
                'db_table': 'o_r_itineraire_itineraire2',
            },
        ),
        migrations.CreateModel(
            name='POI',
            fields=[
                ('published', models.BooleanField(default=False, help_text='Online', verbose_name='Published', db_column=b'public')),
                ('publication_date', models.DateField(verbose_name='Publication date', null=True, editable=False, db_column=b'date_publication', blank=True)),
                ('name', models.CharField(help_text='Public name (Change carefully)', max_length=128, verbose_name='Name', db_column=b'nom')),
                ('review', models.BooleanField(default=False, verbose_name='Waiting for publication', db_column=b'relecture')),
                ('topo_object', models.OneToOneField(parent_link=True, primary_key=True, db_column=b'evenement', serialize=False, to='core.Topology')),
                ('description', models.TextField(help_text='History, details,  ...', verbose_name='Description', db_column=b'description')),
                ('eid', models.CharField(max_length=128, null=True, verbose_name='External id', db_column=b'id_externe', blank=True)),
                ('structure', models.ForeignKey(db_column=b'structure', default=geotrek.authent.models.default_structure_pk, verbose_name='Related structure', to='authent.Structure')),
            ],
            options={
                'db_table': 'o_t_poi',
                'verbose_name': 'POI',
                'verbose_name_plural': 'POI',
            },
            bases=(geotrek.common.mixins.PicturesMixin, mapentity.models.MapEntityMixin, 'core.topology', models.Model),
        ),
        migrations.CreateModel(
            name='POIType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pictogram', models.FileField(max_length=512, null=True, verbose_name='Pictogram', db_column=b'picto', upload_to=b'upload')),
                ('label', models.CharField(max_length=128, verbose_name='Label', db_column=b'nom')),
                ('cirkwi', models.ForeignKey(verbose_name='Cirkwi POI category', blank=True, to='cirkwi.CirkwiPOICategory', null=True)),
            ],
            options={
                'ordering': ['label'],
                'db_table': 'o_b_poi',
                'verbose_name': 'POI type',
                'verbose_name_plural': 'POI types',
            },
        ),
        migrations.CreateModel(
            name='Practice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pictogram', models.FileField(max_length=512, null=True, verbose_name='Pictogram', db_column=b'picto', upload_to=b'upload')),
                ('name', models.CharField(max_length=128, verbose_name='Name', db_column=b'nom')),
                ('distance', models.IntegerField(help_text='Touristic contents and events will associate within this distance (meters)', null=True, verbose_name='Distance', db_column=b'distance', blank=True)),
                ('order', models.IntegerField(help_text='Alphabetical order if blank', null=True, verbose_name='Order', db_column=b'tri', blank=True)),
                ('cirkwi', models.ForeignKey(verbose_name='Cirkwi locomotion', blank=True, to='cirkwi.CirkwiLocomotion', null=True)),
            ],
            options={
                'ordering': ['order', 'name'],
                'db_table': 'o_b_pratique',
                'verbose_name': 'Practice',
                'verbose_name_plural': 'Practices',
            },
        ),
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pictogram', models.FileField(db_column=b'picto', upload_to=b'upload', max_length=512, blank=True, null=True, verbose_name='Pictogram')),
                ('route', models.CharField(max_length=128, verbose_name='Name', db_column=b'parcours')),
            ],
            options={
                'ordering': ['route'],
                'db_table': 'o_b_parcours',
                'verbose_name': 'Route',
                'verbose_name_plural': 'Routes',
            },
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('topo_object', models.OneToOneField(parent_link=True, primary_key=True, db_column=b'evenement', serialize=False, to='core.Topology')),
                ('eid', models.CharField(max_length=128, null=True, verbose_name='External id', db_column=b'id_externe', blank=True)),
                ('structure', models.ForeignKey(db_column=b'structure', default=geotrek.authent.models.default_structure_pk, verbose_name='Related structure', to='authent.Structure')),
            ],
            options={
                'db_table': 'o_t_service',
                'verbose_name': 'Service',
                'verbose_name_plural': 'Services',
            },
            bases=(mapentity.models.MapEntityMixin, 'core.topology', models.Model),
        ),
        migrations.CreateModel(
            name='ServiceType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('published', models.BooleanField(default=False, help_text='Online', verbose_name='Published', db_column=b'public')),
                ('publication_date', models.DateField(verbose_name='Publication date', null=True, editable=False, db_column=b'date_publication', blank=True)),
                ('name', models.CharField(help_text='Public name (Change carefully)', max_length=128, verbose_name='Name', db_column=b'nom')),
                ('review', models.BooleanField(default=False, verbose_name='Waiting for publication', db_column=b'relecture')),
                ('pictogram', models.FileField(max_length=512, null=True, verbose_name='Pictogram', db_column=b'picto', upload_to=b'upload')),
                ('practices', models.ManyToManyField(related_name='services', db_table=b'o_r_service_pratique', verbose_name='Practices', to='trekking.Practice', blank=True)),
            ],
            options={
                'ordering': ['name'],
                'db_table': 'o_b_service',
                'verbose_name': 'Service type',
                'verbose_name_plural': 'Service types',
            },
        ),
        migrations.CreateModel(
            name='Trek',
            fields=[
                ('published', models.BooleanField(default=False, help_text='Online', verbose_name='Published', db_column=b'public')),
                ('publication_date', models.DateField(verbose_name='Publication date', null=True, editable=False, db_column=b'date_publication', blank=True)),
                ('name', models.CharField(help_text='Public name (Change carefully)', max_length=128, verbose_name='Name', db_column=b'nom')),
                ('review', models.BooleanField(default=False, verbose_name='Waiting for publication', db_column=b'relecture')),
                ('topo_object', models.OneToOneField(parent_link=True, primary_key=True, db_column=b'evenement', serialize=False, to='core.Topology')),
                ('departure', models.CharField(help_text='Departure description', max_length=128, verbose_name='Departure', db_column=b'depart', blank=True)),
                ('arrival', models.CharField(help_text='Arrival description', max_length=128, verbose_name='Arrival', db_column=b'arrivee', blank=True)),
                ('description_teaser', models.TextField(help_text='A brief summary (map pop-ups)', verbose_name='Description teaser', db_column=b'chapeau', blank=True)),
                ('description', models.TextField(help_text='Complete description', verbose_name='Description', db_column=b'description', blank=True)),
                ('ambiance', models.TextField(help_text='Main attraction and interest', verbose_name='Ambiance', db_column=b'ambiance', blank=True)),
                ('access', models.TextField(help_text='Best way to go', verbose_name='Access', db_column=b'acces', blank=True)),
                ('disabled_infrastructure', models.TextField(help_text='Any specific infrastructure', verbose_name='Disabled infrastructure', db_column=b'handicap', blank=True)),
                ('duration', models.FloatField(db_column=b'duree', default=0, validators=[django.core.validators.MinValueValidator(0)], blank=True, help_text='In hours (1.5 = 1 h 30, 24 = 1 day, 48 = 2 days)', verbose_name='Duration')),
                ('is_park_centered', models.BooleanField(default=False, help_text='Crosses center of park', verbose_name='Is in the midst of the park', db_column=b'coeur')),
                ('advised_parking', models.CharField(help_text='Where to park', max_length=128, verbose_name='Advised parking', db_column=b'parking', blank=True)),
                ('parking_location', django.contrib.gis.db.models.fields.PointField(db_column=b'geom_parking', verbose_name='Parking location', blank=True, srid=settings.SRID, null=True, spatial_index=False)),
                ('public_transport', models.TextField(help_text='Train, bus (see web links)', verbose_name='Public transport', db_column=b'transport', blank=True)),
                ('advice', models.TextField(help_text='Risks, danger, best period, ...', verbose_name='Advice', db_column=b'recommandation', blank=True)),
                ('points_reference', django.contrib.gis.db.models.fields.MultiPointField(db_column=b'geom_points_reference', verbose_name='Points of reference', blank=True, srid=settings.SRID, null=True, spatial_index=False)),
                ('eid', models.CharField(max_length=128, null=True, verbose_name='External id', db_column=b'id_externe', blank=True)),
                ('eid2', models.CharField(max_length=128, null=True, verbose_name='Second external id', db_column=b'id_externe2', blank=True)),
                ('accessibilities', models.ManyToManyField(related_name='treks', db_table=b'o_r_itineraire_accessibilite', verbose_name='Accessibility', to='trekking.Accessibility', blank=True)),
                ('difficulty', models.ForeignKey(related_name='treks', db_column=b'difficulte', blank=True, to='trekking.DifficultyLevel', null=True, verbose_name='Difficulty')),
                ('information_desks', models.ManyToManyField(related_name='treks', to='tourism.InformationDesk', db_table=b'o_r_itineraire_renseignement', blank=True, help_text='Where to obtain information', verbose_name='Information desks')),
            ],
            options={
                'db_table': 'o_t_itineraire',
                'verbose_name': 'Trek',
                'verbose_name_plural': 'Treks',
            },
            bases=(geotrek.common.mixins.PicturesMixin, mapentity.models.MapEntityMixin, 'core.topology', models.Model),
        ),
        migrations.CreateModel(
            name='TrekNetwork',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pictogram', models.FileField(max_length=512, null=True, verbose_name='Pictogram', db_column=b'picto', upload_to=b'upload')),
                ('network', models.CharField(max_length=128, verbose_name='Name', db_column=b'reseau')),
            ],
            options={
                'ordering': ['network'],
                'db_table': 'o_b_reseau',
                'verbose_name': 'Trek network',
                'verbose_name_plural': 'Trek networks',
            },
        ),
        migrations.CreateModel(
            name='TrekRelationship',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('has_common_departure', models.BooleanField(default=False, verbose_name='Common departure', db_column=b'depart_commun')),
                ('has_common_edge', models.BooleanField(default=False, verbose_name='Common edge', db_column=b'troncons_communs')),
                ('is_circuit_step', models.BooleanField(default=False, verbose_name='Circuit step', db_column=b'etape_circuit')),
                ('trek_a', models.ForeignKey(related_name='trek_relationship_a', db_column=b'itineraire_a', to='trekking.Trek')),
                ('trek_b', models.ForeignKey(related_name='trek_relationship_b', db_column=b'itineraire_b', verbose_name='Trek', to='trekking.Trek')),
            ],
            options={
                'db_table': 'o_r_itineraire_itineraire',
                'verbose_name': 'Trek relationship',
                'verbose_name_plural': 'Trek relationships',
            },
        ),
        migrations.CreateModel(
            name='WebLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128, verbose_name='Name', db_column=b'nom')),
                ('url', models.URLField(max_length=2048, verbose_name='URL', db_column=b'url')),
            ],
            options={
                'ordering': ['name'],
                'db_table': 'o_t_web',
                'verbose_name': 'Web link',
                'verbose_name_plural': 'Web links',
            },
        ),
        migrations.CreateModel(
            name='WebLinkCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pictogram', models.FileField(max_length=512, null=True, verbose_name='Pictogram', db_column=b'picto', upload_to=b'upload')),
                ('label', models.CharField(max_length=128, verbose_name='Label', db_column=b'nom')),
            ],
            options={
                'ordering': ['label'],
                'db_table': 'o_b_web_category',
                'verbose_name': 'Web link category',
                'verbose_name_plural': 'Web link categories',
            },
        ),
        migrations.AddField(
            model_name='weblink',
            name='category',
            field=models.ForeignKey(related_name='links', db_column=b'categorie', blank=True, to='trekking.WebLinkCategory', null=True, verbose_name='Category'),
        ),
        migrations.AddField(
            model_name='trek',
            name='networks',
            field=models.ManyToManyField(related_name='treks', to='trekking.TrekNetwork', db_table=b'o_r_itineraire_reseau', blank=True, help_text='Hiking networks', verbose_name='Networks'),
        ),
        migrations.AddField(
            model_name='trek',
            name='portal',
            field=models.ManyToManyField(related_name='treks', db_table=b'o_r_itineraire_portal', verbose_name='Portal', to='common.TargetPortal', blank=True),
        ),
        migrations.AddField(
            model_name='trek',
            name='practice',
            field=models.ForeignKey(related_name='treks', db_column=b'pratique', blank=True, to='trekking.Practice', null=True, verbose_name='Practice'),
        ),
        migrations.AddField(
            model_name='trek',
            name='related_treks',
            field=models.ManyToManyField(help_text='Connections between treks', related_name='_trek_related_treks_+', verbose_name='Related treks', through='trekking.TrekRelationship', to='trekking.Trek'),
        ),
        migrations.AddField(
            model_name='trek',
            name='route',
            field=models.ForeignKey(related_name='treks', db_column=b'parcours', blank=True, to='trekking.Route', null=True, verbose_name='Route'),
        ),
        migrations.AddField(
            model_name='trek',
            name='source',
            field=models.ManyToManyField(related_name='treks', db_table=b'o_r_itineraire_source', verbose_name='Source', to='common.RecordSource', blank=True),
        ),
        migrations.AddField(
            model_name='trek',
            name='structure',
            field=models.ForeignKey(db_column=b'structure', default=geotrek.authent.models.default_structure_pk, verbose_name='Related structure', to='authent.Structure'),
        ),
        migrations.AddField(
            model_name='trek',
            name='themes',
            field=models.ManyToManyField(related_name='treks', to='common.Theme', db_table=b'o_r_itineraire_theme', blank=True, help_text='Main theme(s)', verbose_name='Themes'),
        ),
        migrations.AddField(
            model_name='trek',
            name='web_links',
            field=models.ManyToManyField(related_name='treks', to='trekking.WebLink', db_table=b'o_r_itineraire_web', blank=True, help_text='External resources', verbose_name='Web links'),
        ),
        migrations.AddField(
            model_name='service',
            name='type',
            field=models.ForeignKey(related_name='services', db_column=b'type', verbose_name='Type', to='trekking.ServiceType'),
        ),
        migrations.AddField(
            model_name='poi',
            name='type',
            field=models.ForeignKey(related_name='pois', db_column=b'type', verbose_name='Type', to='trekking.POIType'),
        ),
        migrations.AddField(
            model_name='orderedtrekchild',
            name='child',
            field=models.ForeignKey(related_name='trek_parents', to='trekking.Trek'),
        ),
        migrations.AddField(
            model_name='orderedtrekchild',
            name='parent',
            field=models.ForeignKey(related_name='trek_children', to='trekking.Trek'),
        ),
        migrations.AlterUniqueTogether(
            name='trekrelationship',
            unique_together=set([('trek_a', 'trek_b')]),
        ),
        migrations.AlterUniqueTogether(
            name='orderedtrekchild',
            unique_together=set([('parent', 'child')]),
        ),
    ]
