# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.conf import settings



class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Trek'
        db.create_table('o_t_itineraire', (
            ('topo_object', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Topology'], unique=True, primary_key=True, db_column='evenement')),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='nom')),
            ('departure', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='depart', blank=True)),
            ('arrival', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='arrivee', blank=True)),
            ('published', self.gf('django.db.models.fields.BooleanField')(db_column='public')),
            ('description_teaser', self.gf('django.db.models.fields.TextField')(db_column='chapeau', blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(db_column='description', blank=True)),
            ('ambiance', self.gf('django.db.models.fields.TextField')(db_column='ambiance', blank=True)),
            ('access', self.gf('django.db.models.fields.TextField')(db_column='acces', blank=True)),
            ('disabled_infrastructure', self.gf('django.db.models.fields.TextField')(db_column='handicap', blank=True)),
            ('duration', self.gf('django.db.models.fields.FloatField')(default=0, null=True, db_column='duree', blank=True)),
            ('is_park_centered', self.gf('django.db.models.fields.BooleanField')(db_column='coeur')),
            ('advised_parking', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='parking', blank=True)),
            ('parking_location', self.gf('django.contrib.gis.db.models.fields.PointField')(srid=settings.SRID, null=True, spatial_index=False, db_column='geom_parking', blank=True)),
            ('public_transport', self.gf('django.db.models.fields.TextField')(db_column='transport', blank=True)),
            ('advice', self.gf('django.db.models.fields.TextField')(db_column='recommandation', blank=True)),
            ('route', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='treks', null=True, db_column='parcours', to=orm['trekking.Route'])),
            ('difficulty', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='treks', null=True, db_column='difficulte', to=orm['trekking.DifficultyLevel'])),
            ('information_desk', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='treks', null=True, db_column='renseignement', to=orm['trekking.InformationDesk'])),
        ))
        db.send_create_signal(u'trekking', ['Trek'])

        # Adding M2M table for field themes on 'Trek'
        m2m_table_name = 'o_r_itineraire_theme'
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('trek', models.ForeignKey(orm[u'trekking.trek'], null=False)),
            ('theme', models.ForeignKey(orm[u'trekking.theme'], null=False))
        ))
        db.create_unique(m2m_table_name, ['trek_id', 'theme_id'])

        # Adding M2M table for field networks on 'Trek'
        m2m_table_name = 'o_r_itineraire_reseau'
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('trek', models.ForeignKey(orm[u'trekking.trek'], null=False)),
            ('treknetwork', models.ForeignKey(orm[u'trekking.treknetwork'], null=False))
        ))
        db.create_unique(m2m_table_name, ['trek_id', 'treknetwork_id'])

        # Adding M2M table for field usages on 'Trek'
        m2m_table_name = 'o_r_itineraire_usage'
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('trek', models.ForeignKey(orm[u'trekking.trek'], null=False)),
            ('usage', models.ForeignKey(orm[u'trekking.usage'], null=False))
        ))
        db.create_unique(m2m_table_name, ['trek_id', 'usage_id'])

        # Adding M2M table for field web_links on 'Trek'
        m2m_table_name = 'o_r_itineraire_web'
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('trek', models.ForeignKey(orm[u'trekking.trek'], null=False)),
            ('weblink', models.ForeignKey(orm[u'trekking.weblink'], null=False))
        ))
        db.create_unique(m2m_table_name, ['trek_id', 'weblink_id'])

        # Adding model 'TrekRelationship'
        db.create_table('o_r_itineraire_itineraire', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('has_common_departure', self.gf('django.db.models.fields.BooleanField')(default=False, db_column='depart_commun')),
            ('has_common_edge', self.gf('django.db.models.fields.BooleanField')(default=False, db_column='troncons_communs')),
            ('is_circuit_step', self.gf('django.db.models.fields.BooleanField')(default=False, db_column='etape_circuit')),
            ('trek_a', self.gf('django.db.models.fields.related.ForeignKey')(related_name='trek_relationship_a', db_column='itineraire_a', to=orm['trekking.Trek'])),
            ('trek_b', self.gf('django.db.models.fields.related.ForeignKey')(related_name='trek_relationship_b', db_column='itineraire_b', to=orm['trekking.Trek'])),
        ))
        db.send_create_signal(u'trekking', ['TrekRelationship'])

        # Adding unique constraint on 'TrekRelationship', fields ['trek_a', 'trek_b']
        db.create_unique('o_r_itineraire_itineraire', ['itineraire_a', 'itineraire_b'])

        # Adding model 'TrekNetwork'
        db.create_table('o_b_reseau', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('network', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='reseau')),
        ))
        db.send_create_signal(u'trekking', ['TrekNetwork'])

        # Adding model 'Usage'
        db.create_table('o_b_usage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('usage', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='usage')),
            ('pictogram', self.gf('django.db.models.fields.files.FileField')(max_length=512, db_column='picto')),
        ))
        db.send_create_signal(u'trekking', ['Usage'])

        # Adding model 'Route'
        db.create_table('o_b_parcours', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('route', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='parcours')),
        ))
        db.send_create_signal(u'trekking', ['Route'])

        # Adding model 'DifficultyLevel'
        db.create_table('o_b_difficulte', (
            ('id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('difficulty', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='difficulte')),
        ))
        db.send_create_signal(u'trekking', ['DifficultyLevel'])

        # Adding model 'WebLink'
        db.create_table('o_t_web', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='nom')),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=128, db_column='url')),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='links', null=True, db_column='categorie', to=orm['trekking.WebLinkCategory'])),
        ))
        db.send_create_signal(u'trekking', ['WebLink'])

        # Adding model 'WebLinkCategory'
        db.create_table('o_b_web_category', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='nom')),
            ('pictogram', self.gf('django.db.models.fields.files.FileField')(max_length=512, db_column='picto')),
        ))
        db.send_create_signal(u'trekking', ['WebLinkCategory'])

        # Adding model 'Theme'
        db.create_table('o_b_theme', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='theme')),
            ('pictogram', self.gf('django.db.models.fields.files.FileField')(max_length=512, db_column='picto')),
        ))
        db.send_create_signal(u'trekking', ['Theme'])

        # Adding model 'InformationDesk'
        db.create_table('o_b_renseignement', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256, db_column='nom')),
            ('description', self.gf('django.db.models.fields.TextField')(db_column='description', blank=True)),
        ))
        db.send_create_signal(u'trekking', ['InformationDesk'])

        # Adding model 'POI'
        db.create_table('o_t_poi', (
            ('topo_object', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Topology'], unique=True, primary_key=True, db_column='evenement')),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='nom')),
            ('description', self.gf('django.db.models.fields.TextField')(db_column='description')),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='pois', db_column='type', to=orm['trekking.POIType'])),
        ))
        db.send_create_signal(u'trekking', ['POI'])

        # Adding model 'POIType'
        db.create_table('o_b_poi', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='nom')),
            ('pictogram', self.gf('django.db.models.fields.files.FileField')(max_length=512, db_column='picto')),
        ))
        db.send_create_signal(u'trekking', ['POIType'])


    def backwards(self, orm):
        # Removing unique constraint on 'TrekRelationship', fields ['trek_a', 'trek_b']
        db.delete_unique('o_r_itineraire_itineraire', ['itineraire_a', 'itineraire_b'])

        # Deleting model 'Trek'
        db.delete_table('o_t_itineraire')

        # Removing M2M table for field themes on 'Trek'
        db.delete_table('o_r_itineraire_theme')

        # Removing M2M table for field networks on 'Trek'
        db.delete_table('o_r_itineraire_reseau')

        # Removing M2M table for field usages on 'Trek'
        db.delete_table('o_r_itineraire_usage')

        # Removing M2M table for field web_links on 'Trek'
        db.delete_table('o_r_itineraire_web')

        # Deleting model 'TrekRelationship'
        db.delete_table('o_r_itineraire_itineraire')

        # Deleting model 'TrekNetwork'
        db.delete_table('o_b_reseau')

        # Deleting model 'Usage'
        db.delete_table('o_b_usage')

        # Deleting model 'Route'
        db.delete_table('o_b_parcours')

        # Deleting model 'DifficultyLevel'
        db.delete_table('o_b_difficulte')

        # Deleting model 'WebLink'
        db.delete_table('o_t_web')

        # Deleting model 'WebLinkCategory'
        db.delete_table('o_b_web_category')

        # Deleting model 'Theme'
        db.delete_table('o_b_theme')

        # Deleting model 'InformationDesk'
        db.delete_table('o_b_renseignement')

        # Deleting model 'POI'
        db.delete_table('o_t_poi')

        # Deleting model 'POIType'
        db.delete_table('o_b_poi')


    models = {
        u'authent.structure': {
            'Meta': {'ordering': "['name']", 'object_name': 'Structure'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'core.comfort': {
            'Meta': {'ordering': "['comfort']", 'object_name': 'Comfort', 'db_table': "'l_b_confort'"},
            'comfort': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "'confort'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['authent.Structure']", 'db_column': "'structure'"})
        },
        u'core.datasource': {
            'Meta': {'ordering': "['source']", 'object_name': 'Datasource', 'db_table': "'l_b_source'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['authent.Structure']", 'db_column': "'structure'"})
        },
        u'core.network': {
            'Meta': {'ordering': "['network']", 'object_name': 'Network', 'db_table': "'l_b_reseau'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'network': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "'reseau'"}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['authent.Structure']", 'db_column': "'structure'"})
        },
        u'core.path': {
            'Meta': {'object_name': 'Path', 'db_table': "'l_t_troncon'"},
            'arrival': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'null': 'True', 'db_column': "'arrivee'", 'blank': 'True'}),
            'ascent': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'db_column': "'denivelee_positive'", 'blank': 'True'}),
            'comfort': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'paths'", 'null': 'True', 'db_column': "'confort'", 'to': u"orm['core.Comfort']"}),
            'comments': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'remarques'", 'blank': 'True'}),
            'datasource': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'paths'", 'null': 'True', 'db_column': "'source'", 'to': u"orm['core.Datasource']"}),
            'date_insert': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_column': "'date_insert'", 'blank': 'True'}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_column': "'date_update'", 'blank': 'True'}),
            'departure': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'null': 'True', 'db_column': "'depart'", 'blank': 'True'}),
            'descent': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'db_column': "'denivelee_negative'", 'blank': 'True'}),
            'geom': ('django.contrib.gis.db.models.fields.LineStringField', [], {'srid': '%s' % settings.SRID, 'spatial_index': 'False'}),
            'geom_3d': ('django.contrib.gis.db.models.fields.GeometryField', [], {'default': 'None', 'dim': '3', 'spatial_index': 'False', 'null': 'True', 'srid': '%s' % settings.SRID}),
            'geom_cadastre': ('django.contrib.gis.db.models.fields.LineStringField', [], {'srid': '%s' % settings.SRID, 'null': 'True', 'spatial_index': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'db_column': "'longueur'", 'blank': 'True'}),
            'max_elevation': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'db_column': "'altitude_maximum'", 'blank': 'True'}),
            'min_elevation': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'db_column': "'altitude_minimum'", 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'networks': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'paths'", 'to': u"orm['core.Network']", 'db_table': "'l_r_troncon_reseau'", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'slope': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'db_column': "'pente'", 'blank': 'True'}),
            'stake': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'paths'", 'null': 'True', 'db_column': "'enjeu'", 'to': u"orm['core.Stake']"}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['authent.Structure']", 'db_column': "'structure'"}),
            'trail': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'paths'", 'null': 'True', 'db_column': "'sentier'", 'to': u"orm['core.Trail']"}),
            'usages': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'paths'", 'to': u"orm['core.Usage']", 'db_table': "'l_r_troncon_usage'", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'valid': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_column': "'valide'"})
        },
        u'core.pathaggregation': {
            'Meta': {'ordering': "['id']", 'object_name': 'PathAggregation', 'db_table': "'e_r_evenement_troncon'"},
            'end_position': ('django.db.models.fields.FloatField', [], {'db_column': "'pk_fin'", 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'db_column': "'ordre'", 'blank': 'True'}),
            'path': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'aggregations'", 'on_delete': 'models.DO_NOTHING', 'db_column': "'troncon'", 'to': u"orm['core.Path']"}),
            'start_position': ('django.db.models.fields.FloatField', [], {'db_column': "'pk_debut'", 'db_index': 'True'}),
            'topo_object': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'aggregations'", 'db_column': "'evenement'", 'to': u"orm['core.Topology']"})
        },
        u'core.stake': {
            'Meta': {'ordering': "['id']", 'object_name': 'Stake', 'db_table': "'l_b_enjeu'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'stake': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "'enjeu'"}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['authent.Structure']", 'db_column': "'structure'"})
        },
        u'core.topology': {
            'Meta': {'object_name': 'Topology', 'db_table': "'e_t_evenement'"},
            'ascent': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'db_column': "'denivelee_positive'", 'blank': 'True'}),
            'date_insert': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_column': "'date_insert'", 'blank': 'True'}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_column': "'date_update'", 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'supprime'"}),
            'descent': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'db_column': "'denivelee_negative'", 'blank': 'True'}),
            'geom': ('django.contrib.gis.db.models.fields.GeometryField', [], {'default': 'None', 'srid': '%s' % settings.SRID, 'null': 'True', 'spatial_index': 'False'}),
            'geom_3d': ('django.contrib.gis.db.models.fields.GeometryField', [], {'default': 'None', 'dim': '3', 'spatial_index': 'False', 'null': 'True', 'srid': '%s' % settings.SRID}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'length': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'db_column': "'longueur'", 'blank': 'True'}),
            'max_elevation': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'db_column': "'altitude_maximum'", 'blank': 'True'}),
            'min_elevation': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'db_column': "'altitude_minimum'", 'blank': 'True'}),
            'offset': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'db_column': "'decallage'"}),
            'paths': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['core.Path']", 'through': u"orm['core.PathAggregation']", 'db_column': "'troncons'", 'symmetrical': 'False'}),
            'slope': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'db_column': "'pente'", 'blank': 'True'})
        },
        u'core.trail': {
            'Meta': {'ordering': "['name']", 'object_name': 'Trail', 'db_table': "'l_t_sentier'"},
            'arrival': ('django.db.models.fields.CharField', [], {'max_length': '64', 'db_column': "'arrivee'"}),
            'comments': ('django.db.models.fields.TextField', [], {'default': "''", 'db_column': "'commentaire'", 'blank': 'True'}),
            'date_insert': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_column': "'date_insert'", 'blank': 'True'}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_column': "'date_update'", 'blank': 'True'}),
            'departure': ('django.db.models.fields.CharField', [], {'max_length': '64', 'db_column': "'depart'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'db_column': "'nom'"}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['authent.Structure']", 'db_column': "'structure'"})
        },
        u'core.usage': {
            'Meta': {'ordering': "['usage']", 'object_name': 'Usage', 'db_table': "'l_b_usage'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['authent.Structure']", 'db_column': "'structure'"}),
            'usage': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "'usage'"})
        },
        u'trekking.difficultylevel': {
            'Meta': {'ordering': "['id']", 'object_name': 'DifficultyLevel', 'db_table': "'o_b_difficulte'"},
            'difficulty': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'difficulte'"}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'})
        },
        u'trekking.informationdesk': {
            'Meta': {'ordering': "['name']", 'object_name': 'InformationDesk', 'db_table': "'o_b_renseignement'"},
            'description': ('django.db.models.fields.TextField', [], {'db_column': "'description'", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'db_column': "'nom'"})
        },
        u'trekking.poi': {
            'Meta': {'object_name': 'POI', 'db_table': "'o_t_poi'", '_ormbases': [u'core.Topology']},
            'description': ('django.db.models.fields.TextField', [], {'db_column': "'description'"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'nom'"}),
            'topo_object': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['core.Topology']", 'unique': 'True', 'primary_key': 'True', 'db_column': "'evenement'"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pois'", 'db_column': "'type'", 'to': u"orm['trekking.POIType']"})
        },
        u'trekking.poitype': {
            'Meta': {'ordering': "['label']", 'object_name': 'POIType', 'db_table': "'o_b_poi'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'nom'"}),
            'pictogram': ('django.db.models.fields.files.FileField', [], {'max_length': '512', 'db_column': "'picto'"})
        },
        u'trekking.route': {
            'Meta': {'ordering': "['route']", 'object_name': 'Route', 'db_table': "'o_b_parcours'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'route': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'parcours'"})
        },
        u'trekking.theme': {
            'Meta': {'ordering': "['label']", 'object_name': 'Theme', 'db_table': "'o_b_theme'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'theme'"}),
            'pictogram': ('django.db.models.fields.files.FileField', [], {'max_length': '512', 'db_column': "'picto'"})
        },
        u'trekking.trek': {
            'Meta': {'object_name': 'Trek', 'db_table': "'o_t_itineraire'", '_ormbases': [u'core.Topology']},
            'access': ('django.db.models.fields.TextField', [], {'db_column': "'acces'", 'blank': 'True'}),
            'advice': ('django.db.models.fields.TextField', [], {'db_column': "'recommandation'", 'blank': 'True'}),
            'advised_parking': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'parking'", 'blank': 'True'}),
            'ambiance': ('django.db.models.fields.TextField', [], {'db_column': "'ambiance'", 'blank': 'True'}),
            'arrival': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'arrivee'", 'blank': 'True'}),
            'departure': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'depart'", 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'db_column': "'description'", 'blank': 'True'}),
            'description_teaser': ('django.db.models.fields.TextField', [], {'db_column': "'chapeau'", 'blank': 'True'}),
            'difficulty': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'treks'", 'null': 'True', 'db_column': "'difficulte'", 'to': u"orm['trekking.DifficultyLevel']"}),
            'disabled_infrastructure': ('django.db.models.fields.TextField', [], {'db_column': "'handicap'", 'blank': 'True'}),
            'duration': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'db_column': "'duree'", 'blank': 'True'}),
            'information_desk': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'treks'", 'null': 'True', 'db_column': "'renseignement'", 'to': u"orm['trekking.InformationDesk']"}),
            'is_park_centered': ('django.db.models.fields.BooleanField', [], {'db_column': "'coeur'"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'nom'"}),
            'networks': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'treks'", 'to': u"orm['trekking.TrekNetwork']", 'db_table': "'o_r_itineraire_reseau'", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'parking_location': ('django.contrib.gis.db.models.fields.PointField', [], {'srid': '%s' % settings.SRID, 'null': 'True', 'spatial_index': 'False', 'db_column': "'geom_parking'", 'blank': 'True'}),
            'public_transport': ('django.db.models.fields.TextField', [], {'db_column': "'transport'", 'blank': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'db_column': "'public'"}),
            'related_treks': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'related_treks+'", 'symmetrical': 'False', 'through': u"orm['trekking.TrekRelationship']", 'to': u"orm['trekking.Trek']"}),
            'route': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'treks'", 'null': 'True', 'db_column': "'parcours'", 'to': u"orm['trekking.Route']"}),
            'themes': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'treks'", 'to': u"orm['trekking.Theme']", 'db_table': "'o_r_itineraire_theme'", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'topo_object': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['core.Topology']", 'unique': 'True', 'primary_key': 'True', 'db_column': "'evenement'"}),
            'usages': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'treks'", 'to': u"orm['trekking.Usage']", 'db_table': "'o_r_itineraire_usage'", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'web_links': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'treks'", 'to': u"orm['trekking.WebLink']", 'db_table': "'o_r_itineraire_web'", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'})
        },
        u'trekking.treknetwork': {
            'Meta': {'ordering': "['network']", 'object_name': 'TrekNetwork', 'db_table': "'o_b_reseau'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'network': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'reseau'"})
        },
        u'trekking.trekrelationship': {
            'Meta': {'unique_together': "(('trek_a', 'trek_b'),)", 'object_name': 'TrekRelationship', 'db_table': "'o_r_itineraire_itineraire'"},
            'has_common_departure': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'depart_commun'"}),
            'has_common_edge': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'troncons_communs'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_circuit_step': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'etape_circuit'"}),
            'trek_a': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'trek_relationship_a'", 'db_column': "'itineraire_a'", 'to': u"orm['trekking.Trek']"}),
            'trek_b': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'trek_relationship_b'", 'db_column': "'itineraire_b'", 'to': u"orm['trekking.Trek']"})
        },
        u'trekking.usage': {
            'Meta': {'ordering': "['usage']", 'object_name': 'Usage', 'db_table': "'o_b_usage'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pictogram': ('django.db.models.fields.files.FileField', [], {'max_length': '512', 'db_column': "'picto'"}),
            'usage': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'usage'"})
        },
        u'trekking.weblink': {
            'Meta': {'object_name': 'WebLink', 'db_table': "'o_t_web'"},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'links'", 'null': 'True', 'db_column': "'categorie'", 'to': u"orm['trekking.WebLinkCategory']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'nom'"}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '128', 'db_column': "'url'"})
        },
        u'trekking.weblinkcategory': {
            'Meta': {'ordering': "['label']", 'object_name': 'WebLinkCategory', 'db_table': "'o_b_web_category'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'nom'"}),
            'pictogram': ('django.db.models.fields.files.FileField', [], {'max_length': '512', 'db_column': "'picto'"})
        }
    }

    complete_apps = ['trekking']