# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Renaming column for 'Stake.stake' to match new field type.
        db.rename_column('l_b_enjeu', 'stake', 'enjeu')
        # Changing field 'Stake.stake'
        db.alter_column('l_b_enjeu', 'enjeu', self.gf('django.db.models.fields.CharField')(max_length=50, db_column='enjeu'))

        # Renaming column for 'Stake.structure' to match new field type.
        db.rename_column('l_b_enjeu', 'structure_id', 'structure')
        # Changing field 'Stake.structure'
        db.alter_column('l_b_enjeu', 'structure', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authent.Structure'], db_column='structure'))

        # Renaming column for 'Network.structure' to match new field type.
        db.rename_column('l_b_reseau', 'structure_id', 'structure')
        # Changing field 'Network.structure'
        db.alter_column('l_b_reseau', 'structure', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authent.Structure'], db_column='structure'))

        # Renaming column for 'Network.network' to match new field type.
        db.rename_column('l_b_reseau', 'network', 'reseau')
        # Changing field 'Network.network'
        db.alter_column('l_b_reseau', 'reseau', self.gf('django.db.models.fields.CharField')(max_length=50, db_column='reseau'))

        # Renaming column for 'Trail.arrival' to match new field type.
        db.rename_column('l_t_sentier', 'arrival', 'arrivee')
        # Changing field 'Trail.arrival'
        db.alter_column('l_t_sentier', 'arrivee', self.gf('django.db.models.fields.CharField')(max_length=64, db_column='arrivee'))

        # Renaming column for 'Trail.name' to match new field type.
        db.rename_column('l_t_sentier', 'name', 'nom')
        # Changing field 'Trail.name'
        db.alter_column('l_t_sentier', 'nom', self.gf('django.db.models.fields.CharField')(max_length=64, db_column='nom'))

        # Renaming column for 'Trail.departure' to match new field type.
        db.rename_column('l_t_sentier', 'departure', 'depart')
        # Changing field 'Trail.departure'
        db.alter_column('l_t_sentier', 'depart', self.gf('django.db.models.fields.CharField')(max_length=64, db_column='depart'))

        # Renaming column for 'Trail.comments' to match new field type.
        db.rename_column('l_t_sentier', 'comments', 'commentaire')
        # Changing field 'Trail.comments'
        db.alter_column('l_t_sentier', 'commentaire', self.gf('django.db.models.fields.TextField')(db_column='commentaire'))

        # Renaming column for 'Trail.structure' to match new field type.
        db.rename_column('l_t_sentier', 'structure_id', 'structure')
        # Changing field 'Trail.structure'
        db.alter_column('l_t_sentier', 'structure', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authent.Structure'], db_column='structure'))

        # Changing field 'Topology.date_update'
        db.alter_column('e_t_evenement', 'date_update', self.gf('django.db.models.fields.DateTimeField')(db_column='date_update'))

        # Changing field 'Topology.date_insert'
        db.alter_column('e_t_evenement', 'date_insert', self.gf('django.db.models.fields.DateTimeField')(db_column='date_insert'))

        # Renaming column for 'Path.comfort' to match new field type.
        db.rename_column('l_t_troncon', 'comfort_id', 'confort')
        # Changing field 'Path.comfort'
        db.alter_column('l_t_troncon', 'confort', self.gf('django.db.models.fields.related.ForeignKey')(null=True, db_column='confort', to=orm['core.Comfort']))

        # Renaming column for 'Path.name' to match new field type.
        db.rename_column('l_t_troncon', 'nom_troncon', 'nom')
        # Changing field 'Path.name'
        db.alter_column('l_t_troncon', 'nom', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, db_column='nom'))

        # Changing field 'Path.date_update'
        db.alter_column('l_t_troncon', 'date_update', self.gf('django.db.models.fields.DateTimeField')(db_column='date_update'))

        # Changing field 'Path.date_insert'
        db.alter_column('l_t_troncon', 'date_insert', self.gf('django.db.models.fields.DateTimeField')(db_column='date_insert'))

        # Renaming column for 'Path.trail' to match new field type.
        db.rename_column('l_t_troncon', 'trail_id', 'sentier')
        # Changing field 'Path.trail'
        db.alter_column('l_t_troncon', 'sentier', self.gf('django.db.models.fields.related.ForeignKey')(null=True, db_column='sentier', to=orm['core.Trail']))

        # Renaming column for 'Path.stake' to match new field type.
        db.rename_column('l_t_troncon', 'stake_id', 'enjeu')
        # Changing field 'Path.stake'
        db.alter_column('l_t_troncon', 'enjeu', self.gf('django.db.models.fields.related.ForeignKey')(null=True, db_column='enjeu', to=orm['core.Stake']))

        # Renaming column for 'Path.datasource' to match new field type.
        db.rename_column('l_t_troncon', 'datasource_id', 'source')
        # Changing field 'Path.datasource'
        db.alter_column('l_t_troncon', 'source', self.gf('django.db.models.fields.related.ForeignKey')(null=True, db_column='source', to=orm['core.Datasource']))

        # Renaming column for 'Path.valid' to match new field type.
        db.rename_column('l_t_troncon', 'troncon_valide', 'valide')
        # Changing field 'Path.valid'
        db.alter_column('l_t_troncon', 'valide', self.gf('django.db.models.fields.BooleanField')(db_column='valide'))

        # Renaming column for 'Path.structure' to match new field type.
        db.rename_column('l_t_troncon', 'structure_id', 'structure')
        # Changing field 'Path.structure'
        db.alter_column('l_t_troncon', 'structure', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authent.Structure'], db_column='structure'))

        # Renaming column for 'Comfort.comfort' to match new field type.
        db.rename_column('l_b_confort', 'comfort', 'confort')
        # Changing field 'Comfort.comfort'
        db.alter_column('l_b_confort', 'confort', self.gf('django.db.models.fields.CharField')(max_length=50, db_column='confort'))

        # Renaming column for 'Comfort.structure' to match new field type.
        db.rename_column('l_b_confort', 'structure_id', 'structure')
        # Changing field 'Comfort.structure'
        db.alter_column('l_b_confort', 'structure', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authent.Structure'], db_column='structure'))

        # Changing field 'Usage.usage'
        db.alter_column('l_b_usage', 'usage', self.gf('django.db.models.fields.CharField')(max_length=50, db_column='usage'))

        # Renaming column for 'Usage.structure' to match new field type.
        db.rename_column('l_b_usage', 'structure_id', 'structure')
        # Changing field 'Usage.structure'
        db.alter_column('l_b_usage', 'structure', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authent.Structure'], db_column='structure'))

        # Renaming column for 'Datasource.structure' to match new field type.
        db.rename_column('l_b_source', 'structure_id', 'structure')
        # Changing field 'Datasource.structure'
        db.alter_column('l_b_source', 'structure', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authent.Structure'], db_column='structure'))

    def backwards(self, orm):

        # Renaming column for 'Stake.stake' to match new field type.
        db.rename_column('l_b_enjeu', 'enjeu', 'stake')
        # Changing field 'Stake.stake'
        db.alter_column('l_b_enjeu', 'stake', self.gf('django.db.models.fields.CharField')(max_length=50))

        # Renaming column for 'Stake.structure' to match new field type.
        db.rename_column('l_b_enjeu', 'structure', 'structure_id')
        # Changing field 'Stake.structure'
        db.alter_column('l_b_enjeu', 'structure_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authent.Structure']))

        # Renaming column for 'Network.structure' to match new field type.
        db.rename_column('l_b_reseau', 'structure', 'structure_id')
        # Changing field 'Network.structure'
        db.alter_column('l_b_reseau', 'structure_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authent.Structure']))

        # Renaming column for 'Network.network' to match new field type.
        db.rename_column('l_b_reseau', 'reseau', 'network')
        # Changing field 'Network.network'
        db.alter_column('l_b_reseau', 'network', self.gf('django.db.models.fields.CharField')(max_length=50))

        # Renaming column for 'Trail.arrival' to match new field type.
        db.rename_column('l_t_sentier', 'arrivee', 'arrival')
        # Changing field 'Trail.arrival'
        db.alter_column('l_t_sentier', 'arrival', self.gf('django.db.models.fields.CharField')(max_length=64))

        # Renaming column for 'Trail.name' to match new field type.
        db.rename_column('l_t_sentier', 'nom', 'name')
        # Changing field 'Trail.name'
        db.alter_column('l_t_sentier', 'name', self.gf('django.db.models.fields.CharField')(max_length=64))

        # Renaming column for 'Trail.departure' to match new field type.
        db.rename_column('l_t_sentier', 'depart', 'departure')
        # Changing field 'Trail.departure'
        db.alter_column('l_t_sentier', 'departure', self.gf('django.db.models.fields.CharField')(max_length=64))

        # Renaming column for 'Trail.comments' to match new field type.
        db.rename_column('l_t_sentier', 'commentaire', 'comments')
        # Changing field 'Trail.comments'
        db.alter_column('l_t_sentier', 'comments', self.gf('django.db.models.fields.TextField')())

        # Renaming column for 'Trail.structure' to match new field type.
        db.rename_column('l_t_sentier', 'structure', 'structure_id')
        # Changing field 'Trail.structure'
        db.alter_column('l_t_sentier', 'structure_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authent.Structure']))

        # Changing field 'Topology.date_update'
        db.alter_column('e_t_evenement', 'date_update', self.gf('django.db.models.fields.DateTimeField')())

        # Changing field 'Topology.date_insert'
        db.alter_column('e_t_evenement', 'date_insert', self.gf('django.db.models.fields.DateTimeField')())

        # Renaming column for 'Path.comfort' to match new field type.
        db.rename_column('l_t_troncon', 'confort', 'comfort_id')
        # Changing field 'Path.comfort'
        db.alter_column('l_t_troncon', 'comfort_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['core.Comfort']))

        # Renaming column for 'Path.name' to match new field type.
        db.rename_column('l_t_troncon', 'nom', 'nom_troncon')
        # Changing field 'Path.name'
        db.alter_column('l_t_troncon', 'nom_troncon', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, db_column='nom_troncon'))

        # Changing field 'Path.date_update'
        db.alter_column('l_t_troncon', 'date_update', self.gf('django.db.models.fields.DateTimeField')())

        # Changing field 'Path.date_insert'
        db.alter_column('l_t_troncon', 'date_insert', self.gf('django.db.models.fields.DateTimeField')())

        # Renaming column for 'Path.trail' to match new field type.
        db.rename_column('l_t_troncon', 'sentier', 'trail_id')
        # Changing field 'Path.trail'
        db.alter_column('l_t_troncon', 'trail_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['core.Trail']))

        # Renaming column for 'Path.stake' to match new field type.
        db.rename_column('l_t_troncon', 'enjeu', 'stake_id')
        # Changing field 'Path.stake'
        db.alter_column('l_t_troncon', 'stake_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['core.Stake']))

        # Renaming column for 'Path.datasource' to match new field type.
        db.rename_column('l_t_troncon', 'source', 'datasource_id')
        # Changing field 'Path.datasource'
        db.alter_column('l_t_troncon', 'datasource_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['core.Datasource']))

        # Renaming column for 'Path.valid' to match new field type.
        db.rename_column('l_t_troncon', 'valide', 'troncon_valide')
        # Changing field 'Path.valid'
        db.alter_column('l_t_troncon', 'troncon_valide', self.gf('django.db.models.fields.BooleanField')(db_column='troncon_valide'))

        # Renaming column for 'Path.structure' to match new field type.
        db.rename_column('l_t_troncon', 'structure', 'structure_id')
        # Changing field 'Path.structure'
        db.alter_column('l_t_troncon', 'structure_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authent.Structure']))

        # Renaming column for 'Comfort.comfort' to match new field type.
        db.rename_column('l_b_confort', 'confort', 'comfort')
        # Changing field 'Comfort.comfort'
        db.alter_column('l_b_confort', 'comfort', self.gf('django.db.models.fields.CharField')(max_length=50))

        # Renaming column for 'Comfort.structure' to match new field type.
        db.rename_column('l_b_confort', 'structure', 'structure_id')
        # Changing field 'Comfort.structure'
        db.alter_column('l_b_confort', 'structure_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authent.Structure']))

        # Changing field 'Usage.usage'
        db.alter_column('l_b_usage', 'usage', self.gf('django.db.models.fields.CharField')(max_length=50))

        # Renaming column for 'Usage.structure' to match new field type.
        db.rename_column('l_b_usage', 'structure', 'structure_id')
        # Changing field 'Usage.structure'
        db.alter_column('l_b_usage', 'structure_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authent.Structure']))

        # Renaming column for 'Datasource.structure' to match new field type.
        db.rename_column('l_b_source', 'structure', 'structure_id')
        # Changing field 'Datasource.structure'
        db.alter_column('l_b_source', 'structure_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authent.Structure']))

    models = {
        'authent.structure': {
            'Meta': {'object_name': 'Structure'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'core.comfort': {
            'Meta': {'object_name': 'Comfort', 'db_table': "'l_b_confort'"},
            'comfort': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "'confort'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']", 'db_column': "'structure'"})
        },
        'core.datasource': {
            'Meta': {'object_name': 'Datasource', 'db_table': "'l_b_source'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']", 'db_column': "'structure'"})
        },
        'core.network': {
            'Meta': {'object_name': 'Network', 'db_table': "'l_b_reseau'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'network': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "'reseau'"}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']", 'db_column': "'structure'"})
        },
        'core.path': {
            'Meta': {'object_name': 'Path', 'db_table': "'l_t_troncon'"},
            'arrival': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'db_column': "'arrivee'", 'blank': 'True'}),
            'ascent': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'denivelee_positive'"}),
            'comfort': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'paths'", 'null': 'True', 'db_column': "'confort'", 'to': "orm['core.Comfort']"}),
            'comments': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'remarques'", 'blank': 'True'}),
            'datasource': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'paths'", 'null': 'True', 'db_column': "'source'", 'to': "orm['core.Datasource']"}),
            'date_insert': ('django.db.models.fields.DateTimeField', [], {'db_column': "'date_insert'"}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {'db_column': "'date_update'"}),
            'departure': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'db_column': "'depart'", 'blank': 'True'}),
            'descent': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'denivelee_negative'"}),
            'geom': ('django.contrib.gis.db.models.fields.LineStringField', [], {'srid': '2154', 'dim': '3', 'spatial_index': 'False'}),
            'geom_cadastre': ('django.contrib.gis.db.models.fields.LineStringField', [], {'srid': '2154', 'dim': '3', 'null': 'True', 'spatial_index': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.FloatField', [], {'default': '0', 'db_column': "'longueur'"}),
            'max_elevation': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'altitude_maximum'"}),
            'min_elevation': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'altitude_minimum'"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'networks': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'paths'", 'to': "orm['core.Network']", 'db_table': "'l_r_troncon_reseau'", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
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
            'path': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'aggregations'", 'on_delete': 'models.DO_NOTHING', 'db_column': "'troncon'", 'to': "orm['core.Path']"}),
            'start_position': ('django.db.models.fields.FloatField', [], {'db_column': "'pk_debut'"}),
            'topo_object': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'aggregations'", 'db_column': "'evenement'", 'to': "orm['core.Topology']"})
        },
        'core.stake': {
            'Meta': {'object_name': 'Stake', 'db_table': "'l_b_enjeu'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'stake': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "'enjeu'"}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']", 'db_column': "'structure'"})
        },
        'core.topology': {
            'Meta': {'object_name': 'Topology', 'db_table': "'e_t_evenement'"},
            'date_insert': ('django.db.models.fields.DateTimeField', [], {'db_column': "'date_insert'"}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {'db_column': "'date_update'"}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'supprime'"}),
            'geom': ('django.contrib.gis.db.models.fields.GeometryField', [], {'srid': '2154', 'dim': '3', 'null': 'True', 'spatial_index': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'length': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'db_column': "'longueur'"}),
            'offset': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'db_column': "'decallage'"}),
            'paths': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Path']", 'through': "orm['core.PathAggregation']", 'db_column': "'troncons'", 'symmetrical': 'False'})
        },
        'core.trail': {
            'Meta': {'object_name': 'Trail', 'db_table': "'l_t_sentier'"},
            'arrival': ('django.db.models.fields.CharField', [], {'max_length': '64', 'db_column': "'arrivee'"}),
            'comments': ('django.db.models.fields.TextField', [], {'default': "''", 'db_column': "'commentaire'"}),
            'departure': ('django.db.models.fields.CharField', [], {'max_length': '64', 'db_column': "'depart'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'db_column': "'nom'"}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']", 'db_column': "'structure'"})
        },
        'core.usage': {
            'Meta': {'object_name': 'Usage', 'db_table': "'l_b_usage'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']", 'db_column': "'structure'"}),
            'usage': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_column': "'usage'"})
        }
    }

    complete_apps = ['core']