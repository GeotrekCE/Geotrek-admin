# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Trek.name_es'
        db.add_column('o_t_itineraire', 'name_es',
                      self.gf('django.db.models.fields.CharField')(max_length=128, null=True, db_column='nom_es', blank=True),
                      keep_default=False)

        # Adding field 'Trek.departure_es'
        db.add_column('o_t_itineraire', 'departure_es',
                      self.gf('django.db.models.fields.CharField')(max_length=128, null=True, db_column='depart_es', blank=True),
                      keep_default=False)

        # Adding field 'Trek.arrival_es'
        db.add_column('o_t_itineraire', 'arrival_es',
                      self.gf('django.db.models.fields.CharField')(max_length=128, null=True, db_column='arrivee_es', blank=True),
                      keep_default=False)

        # Adding field 'Trek.description_teaser_es'
        db.add_column('o_t_itineraire', 'description_teaser_es',
                      self.gf('django.db.models.fields.TextField')(null=True, db_column='chapeau_es', blank=True),
                      keep_default=False)

        # Adding field 'Trek.description_es'
        db.add_column('o_t_itineraire', 'description_es',
                      self.gf('django.db.models.fields.TextField')(null=True, db_column='description_es', blank=True),
                      keep_default=False)

        # Adding field 'Trek.ambiance_es'
        db.add_column('o_t_itineraire', 'ambiance_es',
                      self.gf('django.db.models.fields.TextField')(null=True, db_column='ambiance_es', blank=True),
                      keep_default=False)

        # Adding field 'Trek.access_es'
        db.add_column('o_t_itineraire', 'access_es',
                      self.gf('django.db.models.fields.TextField')(null=True, db_column='acces_es', blank=True),
                      keep_default=False)

        # Adding field 'Trek.disabled_infrastructure_es'
        db.add_column('o_t_itineraire', 'disabled_infrastructure_es',
                      self.gf('django.db.models.fields.TextField')(null=True, db_column='handicap_es', blank=True),
                      keep_default=False)

        # Adding field 'Trek.advice_es'
        db.add_column('o_t_itineraire', 'advice_es',
                      self.gf('django.db.models.fields.TextField')(null=True, db_column='recommandation_es', blank=True),
                      keep_default=False)

        # Adding field 'TrekNetwork.network_es'
        db.add_column('o_b_reseau', 'network_es',
                      self.gf('django.db.models.fields.CharField')(max_length=128, null=True, db_column='reseau_es', blank=True),
                      keep_default=False)

        # Adding field 'Usage.usage_es'
        db.add_column('o_b_usage', 'usage_es',
                      self.gf('django.db.models.fields.CharField')(max_length=128, null=True, db_column='usage_es', blank=True),
                      keep_default=False)

        # Adding field 'WebLink.name_es'
        db.add_column('o_t_web', 'name_es',
                      self.gf('django.db.models.fields.CharField')(max_length=128, null=True, db_column='nom_es', blank=True),
                      keep_default=False)

        # Adding field 'Route.route_es'
        db.add_column('o_b_parcours', 'route_es',
                      self.gf('django.db.models.fields.CharField')(max_length=128, null=True, db_column='parcours_es', blank=True),
                      keep_default=False)

        # Adding field 'Theme.label_es'
        db.add_column('o_b_theme', 'label_es',
                      self.gf('django.db.models.fields.CharField')(max_length=128, null=True, db_column='theme_es', blank=True),
                      keep_default=False)

        # Adding field 'DifficultyLevel.difficulty_es'
        db.add_column('o_b_difficulte', 'difficulty_es',
                      self.gf('django.db.models.fields.CharField')(max_length=128, null=True, db_column='difficulte_es', blank=True),
                      keep_default=False)

        # Adding field 'WebLinkCategory.label_es'
        db.add_column('o_b_web_category', 'label_es',
                      self.gf('django.db.models.fields.CharField')(max_length=128, null=True, db_column='nom_es', blank=True),
                      keep_default=False)

        # Adding field 'POI.name_es'
        db.add_column('o_t_poi', 'name_es',
                      self.gf('django.db.models.fields.CharField')(max_length=128, null=True, db_column='nom_es', blank=True),
                      keep_default=False)

        # Adding field 'POI.description_es'
        db.add_column('o_t_poi', 'description_es',
                      self.gf('django.db.models.fields.TextField')(null=True, db_column='description_es', blank=True),
                      keep_default=False)

        # Adding field 'InformationDesk.name_es'
        db.add_column('o_b_renseignement', 'name_es',
                      self.gf('django.db.models.fields.CharField')(max_length=256, null=True, db_column='nom_es', blank=True),
                      keep_default=False)

        # Adding field 'InformationDesk.description_es'
        db.add_column('o_b_renseignement', 'description_es',
                      self.gf('django.db.models.fields.TextField')(null=True, db_column='description_es', blank=True),
                      keep_default=False)

        # Adding field 'POIType.label_es'
        db.add_column('o_b_poi', 'label_es',
                      self.gf('django.db.models.fields.CharField')(max_length=128, null=True, db_column='nom_es', blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Trek.name_es'
        db.delete_column('o_t_itineraire', 'nom_es')

        # Deleting field 'Trek.departure_es'
        db.delete_column('o_t_itineraire', 'depart_es')

        # Deleting field 'Trek.arrival_es'
        db.delete_column('o_t_itineraire', 'arrivee_es')

        # Deleting field 'Trek.description_teaser_es'
        db.delete_column('o_t_itineraire', 'chapeau_es')

        # Deleting field 'Trek.description_es'
        db.delete_column('o_t_itineraire', 'description_es')

        # Deleting field 'Trek.ambiance_es'
        db.delete_column('o_t_itineraire', 'ambiance_es')

        # Deleting field 'Trek.access_es'
        db.delete_column('o_t_itineraire', 'acces_es')

        # Deleting field 'Trek.disabled_infrastructure_es'
        db.delete_column('o_t_itineraire', 'handicap_es')

        # Deleting field 'Trek.advice_es'
        db.delete_column('o_t_itineraire', 'recommandation_es')

        # Deleting field 'TrekNetwork.network_es'
        db.delete_column('o_b_reseau', 'reseau_es')

        # Deleting field 'Usage.usage_es'
        db.delete_column('o_b_usage', 'usage_es')

        # Deleting field 'WebLink.name_es'
        db.delete_column('o_t_web', 'nom_es')

        # Deleting field 'Route.route_es'
        db.delete_column('o_b_parcours', 'parcours_es')

        # Deleting field 'Theme.label_es'
        db.delete_column('o_b_theme', 'theme_es')

        # Deleting field 'DifficultyLevel.difficulty_es'
        db.delete_column('o_b_difficulte', 'difficulte_es')

        # Deleting field 'WebLinkCategory.label_es'
        db.delete_column('o_b_web_category', 'nom_es')

        # Deleting field 'POI.name_es'
        db.delete_column('o_t_poi', 'nom_es')

        # Deleting field 'POI.description_es'
        db.delete_column('o_t_poi', 'description_es')

        # Deleting field 'InformationDesk.name_es'
        db.delete_column('o_b_renseignement', 'nom_es')

        # Deleting field 'InformationDesk.description_es'
        db.delete_column('o_b_renseignement', 'description_es')

        # Deleting field 'POIType.label_es'
        db.delete_column('o_b_poi', 'nom_es')


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
            'geom': ('django.contrib.gis.db.models.fields.LineStringField', [], {'srid': '2154', 'spatial_index': 'False'}),
            'geom_3d': ('django.contrib.gis.db.models.fields.GeometryField', [], {'default': 'None', 'dim': '3', 'spatial_index': 'False', 'null': 'True', 'srid': '2154'}),
            'geom_cadastre': ('django.contrib.gis.db.models.fields.LineStringField', [], {'srid': '2154', 'null': 'True', 'spatial_index': 'False'}),
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
            'geom': ('django.contrib.gis.db.models.fields.GeometryField', [], {'default': 'None', 'srid': '2154', 'null': 'True', 'spatial_index': 'False'}),
            'geom_3d': ('django.contrib.gis.db.models.fields.GeometryField', [], {'default': 'None', 'dim': '3', 'spatial_index': 'False', 'null': 'True', 'srid': '2154'}),
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
            'difficulty_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'difficulte'", 'blank': 'True'}),
            'difficulty_es': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'difficulte'", 'blank': 'True'}),
            'difficulty_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'difficulte'", 'blank': 'True'}),
            'difficulty_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'difficulte'", 'blank': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'})
        },
        u'trekking.informationdesk': {
            'Meta': {'ordering': "['name']", 'object_name': 'InformationDesk', 'db_table': "'o_b_renseignement'"},
            'description': ('django.db.models.fields.TextField', [], {'db_column': "'description'", 'blank': 'True'}),
            'description_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'description'", 'blank': 'True'}),
            'description_es': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'description'", 'blank': 'True'}),
            'description_fr': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'description'", 'blank': 'True'}),
            'description_it': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'description'", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'db_column': "'nom'"}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'name_es': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'name_fr': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'name_it': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'})
        },
        u'trekking.poi': {
            'Meta': {'object_name': 'POI', 'db_table': "'o_t_poi'", '_ormbases': [u'core.Topology']},
            'description': ('django.db.models.fields.TextField', [], {'db_column': "'description'"}),
            'description_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'description'", 'blank': 'True'}),
            'description_es': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'description'", 'blank': 'True'}),
            'description_fr': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'description'", 'blank': 'True'}),
            'description_it': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'description'", 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'nom'"}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'name_es': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'name_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'name_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'topo_object': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['core.Topology']", 'unique': 'True', 'primary_key': 'True', 'db_column': "'evenement'"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pois'", 'db_column': "'type'", 'to': u"orm['trekking.POIType']"})
        },
        u'trekking.poitype': {
            'Meta': {'ordering': "['label']", 'object_name': 'POIType', 'db_table': "'o_b_poi'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'nom'"}),
            'label_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'label_es': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'label_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'label_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'pictogram': ('django.db.models.fields.files.FileField', [], {'max_length': '512', 'db_column': "'picto'"})
        },
        u'trekking.route': {
            'Meta': {'ordering': "['route']", 'object_name': 'Route', 'db_table': "'o_b_parcours'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'route': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'parcours'"}),
            'route_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'parcours'", 'blank': 'True'}),
            'route_es': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'parcours'", 'blank': 'True'}),
            'route_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'parcours'", 'blank': 'True'}),
            'route_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'parcours'", 'blank': 'True'})
        },
        u'trekking.theme': {
            'Meta': {'ordering': "['label']", 'object_name': 'Theme', 'db_table': "'o_b_theme'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'theme'"}),
            'label_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'theme'", 'blank': 'True'}),
            'label_es': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'theme'", 'blank': 'True'}),
            'label_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'theme'", 'blank': 'True'}),
            'label_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'theme'", 'blank': 'True'}),
            'pictogram': ('django.db.models.fields.files.FileField', [], {'max_length': '512', 'db_column': "'picto'"})
        },
        u'trekking.trek': {
            'Meta': {'object_name': 'Trek', 'db_table': "'o_t_itineraire'", '_ormbases': [u'core.Topology']},
            'access': ('django.db.models.fields.TextField', [], {'db_column': "'acces'", 'blank': 'True'}),
            'access_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'acces'", 'blank': 'True'}),
            'access_es': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'acces'", 'blank': 'True'}),
            'access_fr': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'acces'", 'blank': 'True'}),
            'access_it': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'acces'", 'blank': 'True'}),
            'advice': ('django.db.models.fields.TextField', [], {'db_column': "'recommandation'", 'blank': 'True'}),
            'advice_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'recommandation'", 'blank': 'True'}),
            'advice_es': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'recommandation'", 'blank': 'True'}),
            'advice_fr': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'recommandation'", 'blank': 'True'}),
            'advice_it': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'recommandation'", 'blank': 'True'}),
            'advised_parking': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'parking'", 'blank': 'True'}),
            'ambiance': ('django.db.models.fields.TextField', [], {'db_column': "'ambiance'", 'blank': 'True'}),
            'ambiance_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'ambiance'", 'blank': 'True'}),
            'ambiance_es': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'ambiance'", 'blank': 'True'}),
            'ambiance_fr': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'ambiance'", 'blank': 'True'}),
            'ambiance_it': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'ambiance'", 'blank': 'True'}),
            'arrival': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'arrivee'", 'blank': 'True'}),
            'arrival_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'arrivee'", 'blank': 'True'}),
            'arrival_es': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'arrivee'", 'blank': 'True'}),
            'arrival_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'arrivee'", 'blank': 'True'}),
            'arrival_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'arrivee'", 'blank': 'True'}),
            'departure': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'depart'", 'blank': 'True'}),
            'departure_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'depart'", 'blank': 'True'}),
            'departure_es': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'depart'", 'blank': 'True'}),
            'departure_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'depart'", 'blank': 'True'}),
            'departure_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'depart'", 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'db_column': "'description'", 'blank': 'True'}),
            'description_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'description'", 'blank': 'True'}),
            'description_es': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'description'", 'blank': 'True'}),
            'description_fr': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'description'", 'blank': 'True'}),
            'description_it': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'description'", 'blank': 'True'}),
            'description_teaser': ('django.db.models.fields.TextField', [], {'db_column': "'chapeau'", 'blank': 'True'}),
            'description_teaser_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'chapeau'", 'blank': 'True'}),
            'description_teaser_es': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'chapeau'", 'blank': 'True'}),
            'description_teaser_fr': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'chapeau'", 'blank': 'True'}),
            'description_teaser_it': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'chapeau'", 'blank': 'True'}),
            'difficulty': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'treks'", 'null': 'True', 'db_column': "'difficulte'", 'to': u"orm['trekking.DifficultyLevel']"}),
            'disabled_infrastructure': ('django.db.models.fields.TextField', [], {'db_column': "'handicap'", 'blank': 'True'}),
            'disabled_infrastructure_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'handicap'", 'blank': 'True'}),
            'disabled_infrastructure_es': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'handicap'", 'blank': 'True'}),
            'disabled_infrastructure_fr': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'handicap'", 'blank': 'True'}),
            'disabled_infrastructure_it': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'handicap'", 'blank': 'True'}),
            'duration': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'db_column': "'duree'", 'blank': 'True'}),
            'information_desk': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'treks'", 'null': 'True', 'db_column': "'renseignement'", 'to': u"orm['trekking.InformationDesk']"}),
            'is_park_centered': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'coeur'"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'nom'"}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'name_es': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'name_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'name_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'networks': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'treks'", 'to': u"orm['trekking.TrekNetwork']", 'db_table': "'o_r_itineraire_reseau'", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'parking_location': ('django.contrib.gis.db.models.fields.PointField', [], {'srid': '2154', 'null': 'True', 'spatial_index': 'False', 'db_column': "'geom_parking'", 'blank': 'True'}),
            'public_transport': ('django.db.models.fields.TextField', [], {'db_column': "'transport'", 'blank': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'public'"}),
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
            'network': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'reseau'"}),
            'network_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'reseau'", 'blank': 'True'}),
            'network_es': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'reseau'", 'blank': 'True'}),
            'network_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'reseau'", 'blank': 'True'}),
            'network_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'reseau'", 'blank': 'True'})
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
            'usage': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'usage'"}),
            'usage_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'usage'", 'blank': 'True'}),
            'usage_es': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'usage'", 'blank': 'True'}),
            'usage_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'usage'", 'blank': 'True'}),
            'usage_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'usage'", 'blank': 'True'})
        },
        u'trekking.weblink': {
            'Meta': {'object_name': 'WebLink', 'db_table': "'o_t_web'"},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'links'", 'null': 'True', 'db_column': "'categorie'", 'to': u"orm['trekking.WebLinkCategory']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'nom'"}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'name_es': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'name_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'name_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '128', 'db_column': "'url'"})
        },
        u'trekking.weblinkcategory': {
            'Meta': {'ordering': "['label']", 'object_name': 'WebLinkCategory', 'db_table': "'o_b_web_category'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'nom'"}),
            'label_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'label_es': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'label_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'label_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'pictogram': ('django.db.models.fields.files.FileField', [], {'max_length': '512', 'db_column': "'picto'"})
        }
    }

    complete_apps = ['trekking']
