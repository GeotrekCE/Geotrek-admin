# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models, connection
from django.conf import settings
from django.db.utils import DatabaseError


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Topology.slope'
        try:
            db.execute("DROP TRIGGER IF EXISTS m_t_evenement_interventions_iu_tgr ON e_t_evenement;")
        except DatabaseError:
            connection.close()
            pass

        db.alter_column('e_t_evenement', 'pente', self.gf('django.db.models.fields.FloatField')(null=True, db_column='pente'))

        # Changing field 'Topology.descent'
        db.alter_column('e_t_evenement', 'denivelee_negative', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='denivelee_negative'))

        # Changing field 'Topology.length'
        db.alter_column('e_t_evenement', 'longueur', self.gf('django.db.models.fields.FloatField')(null=True, db_column='longueur'))

        # Changing field 'Topology.max_elevation'
        db.alter_column('e_t_evenement', 'altitude_maximum', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='altitude_maximum'))

        # Changing field 'Topology.ascent'
        db.alter_column('e_t_evenement', 'denivelee_positive', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='denivelee_positive'))

        # Changing field 'Topology.min_elevation'
        db.alter_column('e_t_evenement', 'altitude_minimum', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='altitude_minimum'))

        # Changing field 'Path.slope'
        db.alter_column('l_t_troncon', 'pente', self.gf('django.db.models.fields.FloatField')(null=True, db_column='pente'))

        # Changing field 'Path.arrival'
        db.alter_column('l_t_troncon', 'arrivee', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, db_column='arrivee'))

        # Changing field 'Path.descent'
        db.alter_column('l_t_troncon', 'denivelee_negative', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='denivelee_negative'))

        # Changing field 'Path.min_elevation'
        db.alter_column('l_t_troncon', 'altitude_minimum', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='altitude_minimum'))

        # Changing field 'Path.departure'
        db.alter_column('l_t_troncon', 'depart', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, db_column='depart'))

        # Changing field 'Path.length'
        db.alter_column('l_t_troncon', 'longueur', self.gf('django.db.models.fields.FloatField')(null=True, db_column='longueur'))

        # Changing field 'Path.ascent'
        db.alter_column('l_t_troncon', 'denivelee_positive', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='denivelee_positive'))

        # Changing field 'Path.max_elevation'
        db.alter_column('l_t_troncon', 'altitude_maximum', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='altitude_maximum'))

    def backwards(self, orm):

        # Changing field 'Topology.slope'
        db.alter_column('e_t_evenement', 'pente', self.gf('django.db.models.fields.FloatField')(db_column='pente'))

        # Changing field 'Topology.descent'
        db.alter_column('e_t_evenement', 'denivelee_negative', self.gf('django.db.models.fields.IntegerField')(db_column='denivelee_negative'))

        # Changing field 'Topology.length'
        db.alter_column('e_t_evenement', 'longueur', self.gf('django.db.models.fields.FloatField')(db_column='longueur'))

        # Changing field 'Topology.max_elevation'
        db.alter_column('e_t_evenement', 'altitude_maximum', self.gf('django.db.models.fields.IntegerField')(db_column='altitude_maximum'))

        # Changing field 'Topology.ascent'
        db.alter_column('e_t_evenement', 'denivelee_positive', self.gf('django.db.models.fields.IntegerField')(db_column='denivelee_positive'))

        # Changing field 'Topology.min_elevation'
        db.alter_column('e_t_evenement', 'altitude_minimum', self.gf('django.db.models.fields.IntegerField')(db_column='altitude_minimum'))

        # Changing field 'Path.slope'
        db.alter_column('l_t_troncon', 'pente', self.gf('django.db.models.fields.FloatField')(db_column='pente'))

        # Changing field 'Path.arrival'
        db.alter_column('l_t_troncon', 'arrivee', self.gf('django.db.models.fields.CharField')(max_length=250, db_column='arrivee'))

        # Changing field 'Path.descent'
        db.alter_column('l_t_troncon', 'denivelee_negative', self.gf('django.db.models.fields.IntegerField')(db_column='denivelee_negative'))

        # Changing field 'Path.min_elevation'
        db.alter_column('l_t_troncon', 'altitude_minimum', self.gf('django.db.models.fields.IntegerField')(db_column='altitude_minimum'))

        # Changing field 'Path.departure'
        db.alter_column('l_t_troncon', 'depart', self.gf('django.db.models.fields.CharField')(max_length=250, db_column='depart'))

        # Changing field 'Path.length'
        db.alter_column('l_t_troncon', 'longueur', self.gf('django.db.models.fields.FloatField')(db_column='longueur'))

        # Changing field 'Path.ascent'
        db.alter_column('l_t_troncon', 'denivelee_positive', self.gf('django.db.models.fields.IntegerField')(db_column='denivelee_positive'))

        # Changing field 'Path.max_elevation'
        db.alter_column('l_t_troncon', 'altitude_maximum', self.gf('django.db.models.fields.IntegerField')(db_column='altitude_maximum'))

    models = {
        'authent.structure': {
            'Meta': {'ordering': "['name']", 'object_name': 'Structure'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'core.comfort': {
            'Meta': {'ordering': "['comfort']", 'object_name': 'Comfort', 'db_table': "'l_b_confort'"},
            'comfort': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "'confort'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']", 'db_column': "'structure'"})
        },
        'core.datasource': {
            'Meta': {'ordering': "['source']", 'object_name': 'Datasource', 'db_table': "'l_b_source'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']", 'db_column': "'structure'"})
        },
        'core.network': {
            'Meta': {'ordering': "['network']", 'object_name': 'Network', 'db_table': "'l_b_reseau'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'network': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "'reseau'"}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']", 'db_column': "'structure'"})
        },
        'core.path': {
            'Meta': {'object_name': 'Path', 'db_table': "'l_t_troncon'"},
            'arrival': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'null': 'True', 'db_column': "'arrivee'", 'blank': 'True'}),
            'ascent': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'db_column': "'denivelee_positive'", 'blank': 'True'}),
            'comfort': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'paths'", 'null': 'True', 'db_column': "'confort'", 'to': "orm['core.Comfort']"}),
            'comments': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'remarques'", 'blank': 'True'}),
            'datasource': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'paths'", 'null': 'True', 'db_column': "'source'", 'to': "orm['core.Datasource']"}),
            'date_insert': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_column': "'date_insert'", 'blank': 'True'}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_column': "'date_update'", 'blank': 'True'}),
            'departure': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'null': 'True', 'db_column': "'depart'", 'blank': 'True'}),
            'descent': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'db_column': "'denivelee_negative'", 'blank': 'True'}),
            'geom': ('django.contrib.gis.db.models.fields.LineStringField', [], {'srid': '%s' % settings.SRID, 'dim': '3', 'spatial_index': 'False'}),
            'geom_cadastre': ('django.contrib.gis.db.models.fields.LineStringField', [], {'srid': '%s' % settings.SRID, 'dim': '3', 'null': 'True', 'spatial_index': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'db_column': "'longueur'", 'blank': 'True'}),
            'max_elevation': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'db_column': "'altitude_maximum'", 'blank': 'True'}),
            'min_elevation': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'db_column': "'altitude_minimum'", 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'networks': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'paths'", 'to': "orm['core.Network']", 'db_table': "'l_r_troncon_reseau'", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'slope': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'db_column': "'pente'", 'blank': 'True'}),
            'stake': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'paths'", 'null': 'True', 'db_column': "'enjeu'", 'to': "orm['core.Stake']"}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']", 'db_column': "'structure'"}),
            'trail': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'paths'", 'null': 'True', 'db_column': "'sentier'", 'to': "orm['core.Trail']"}),
            'usages': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'paths'", 'to': "orm['core.Usage']", 'db_table': "'l_r_troncon_usage'", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'valid': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_column': "'valide'"})
        },
        'core.pathaggregation': {
            'Meta': {'ordering': "['id']", 'object_name': 'PathAggregation', 'db_table': "'e_r_evenement_troncon'"},
            'end_position': ('django.db.models.fields.FloatField', [], {'db_column': "'pk_fin'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'db_column': "'ordre'", 'blank': 'True'}),
            'path': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'aggregations'", 'on_delete': 'models.DO_NOTHING', 'db_column': "'troncon'", 'to': "orm['core.Path']"}),
            'start_position': ('django.db.models.fields.FloatField', [], {'db_column': "'pk_debut'"}),
            'topo_object': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'aggregations'", 'db_column': "'evenement'", 'to': "orm['core.Topology']"})
        },
        'core.stake': {
            'Meta': {'ordering': "['stake']", 'object_name': 'Stake', 'db_table': "'l_b_enjeu'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'stake': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "'enjeu'"}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']", 'db_column': "'structure'"})
        },
        'core.topology': {
            'Meta': {'object_name': 'Topology', 'db_table': "'e_t_evenement'"},
            'ascent': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'db_column': "'denivelee_positive'", 'blank': 'True'}),
            'date_insert': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_column': "'date_insert'", 'blank': 'True'}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_column': "'date_update'", 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'supprime'"}),
            'descent': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'db_column': "'denivelee_negative'", 'blank': 'True'}),
            'geom': ('django.contrib.gis.db.models.fields.GeometryField', [], {'srid': '%s' % settings.SRID, 'dim': '3', 'null': 'True', 'spatial_index': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'length': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'db_column': "'longueur'", 'blank': 'True'}),
            'max_elevation': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'db_column': "'altitude_maximum'", 'blank': 'True'}),
            'min_elevation': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'db_column': "'altitude_minimum'", 'blank': 'True'}),
            'offset': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'db_column': "'decallage'"}),
            'paths': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Path']", 'through': "orm['core.PathAggregation']", 'db_column': "'troncons'", 'symmetrical': 'False'}),
            'slope': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True', 'db_column': "'pente'", 'blank': 'True'})
        },
        'core.trail': {
            'Meta': {'ordering': "['name']", 'object_name': 'Trail', 'db_table': "'l_t_sentier'"},
            'arrival': ('django.db.models.fields.CharField', [], {'max_length': '64', 'db_column': "'arrivee'"}),
            'comments': ('django.db.models.fields.TextField', [], {'default': "''", 'db_column': "'commentaire'", 'blank': 'True'}),
            'departure': ('django.db.models.fields.CharField', [], {'max_length': '64', 'db_column': "'depart'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'db_column': "'nom'"}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']", 'db_column': "'structure'"})
        },
        'core.usage': {
            'Meta': {'ordering': "['usage']", 'object_name': 'Usage', 'db_table': "'l_b_usage'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']", 'db_column': "'structure'"}),
            'usage': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "'usage'"})
        }
    }

    complete_apps = ['core']