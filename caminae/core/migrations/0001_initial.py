# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    depends_on = (
       ("maintenance", "0003_auto__add_field_interventiontypology_typology_en__add_field_interventi"),
    )

    def forwards(self, orm):
        # Adding model 'Path'
        db.create_table('troncons', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('structure', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['authent.Structure'])),
            ('geom', self.gf('django.contrib.gis.db.models.fields.LineStringField')(srid=2154, spatial_index=False)),
            ('geom_cadastre', self.gf('django.contrib.gis.db.models.fields.LineStringField')(null=True, srid=2154, spatial_index=False)),
            ('date_insert', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('date_update', self.gf('django.db.models.fields.DateField')(auto_now=True, blank=True)),
            ('valid', self.gf('django.db.models.fields.BooleanField')(default=True, db_column='troncon_valide')),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, db_column='nom_troncon')),
            ('comments', self.gf('django.db.models.fields.TextField')(null=True, db_column='remarques')),
            ('length', self.gf('django.db.models.fields.IntegerField')(default=0, db_column='longueur')),
            ('ascent', self.gf('django.db.models.fields.IntegerField')(default=0, db_column='denivelee_positive')),
            ('descent', self.gf('django.db.models.fields.IntegerField')(default=0, db_column='denivelee_negative')),
            ('min_elevation', self.gf('django.db.models.fields.IntegerField')(default=0, db_column='altitude_minimum')),
            ('max_elevation', self.gf('django.db.models.fields.IntegerField')(default=0, db_column='altitude_maximum')),
        ))
        db.send_create_signal('core', ['Path'])

        # Adding model 'TopologyMixin'
        db.create_table('evenements', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date_insert', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('date_update', self.gf('django.db.models.fields.DateField')(auto_now=True, blank=True)),
            ('offset', self.gf('django.db.models.fields.IntegerField')(db_column='decallage')),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False, db_column='supprime')),
            ('length', self.gf('django.db.models.fields.FloatField')(db_column='longueur')),
            ('geom', self.gf('django.contrib.gis.db.models.fields.LineStringField')(srid=2154, spatial_index=False)),
            ('kind', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.TopologyMixinKind'])),
        ))
        db.send_create_signal('core', ['TopologyMixin'])

        # Adding M2M table for field interventions on 'TopologyMixin'
        db.create_table('evenements_interventions', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('topologymixin', models.ForeignKey(orm['core.topologymixin'], null=False)),
            ('intervention', models.ForeignKey(orm['maintenance.intervention'], null=False))
        ))
        db.create_unique('evenements_interventions', ['topologymixin_id', 'intervention_id'])

        # Adding model 'TopologyMixinKind'
        db.create_table('type_evenements', (
            ('code', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('kind', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal('core', ['TopologyMixinKind'])

        # Adding model 'PathAggregation'
        db.create_table('evenements_troncons', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('path', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Path'], db_column='troncon')),
            ('topo_object', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.TopologyMixin'], db_column='evenement')),
            ('start_position', self.gf('django.db.models.fields.FloatField')(db_column='pk_debut')),
            ('end_position', self.gf('django.db.models.fields.FloatField')(db_column='pk_fin')),
        ))
        db.send_create_signal('core', ['PathAggregation'])


    def backwards(self, orm):
        # Deleting model 'Path'
        db.delete_table('troncons')

        # Deleting model 'TopologyMixin'
        db.delete_table('evenements')

        # Removing M2M table for field interventions on 'TopologyMixin'
        db.delete_table('evenements_interventions')

        # Deleting model 'TopologyMixinKind'
        db.delete_table('type_evenements')

        # Deleting model 'PathAggregation'
        db.delete_table('evenements_troncons')


    models = {
        'authent.structure': {
            'Meta': {'object_name': 'Structure'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'core.path': {
            'Meta': {'object_name': 'Path', 'db_table': "'troncons'"},
            'ascent': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'denivelee_positive'"}),
            'comments': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'remarques'"}),
            'date_insert': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_update': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'descent': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'denivelee_negative'"}),
            'geom': ('django.contrib.gis.db.models.fields.LineStringField', [], {'spatial_index': 'False'}),
            'geom_cadastre': ('django.contrib.gis.db.models.fields.LineStringField', [], {'null': 'True', 'spatial_index': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'longueur'"}),
            'max_elevation': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'altitude_maximum'"}),
            'min_elevation': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'altitude_minimum'"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'db_column': "'nom_troncon'"}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']"}),
            'valid': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_column': "'troncon_valide'"})
        },
        'core.pathaggregation': {
            'Meta': {'object_name': 'PathAggregation', 'db_table': "'evenements_troncons'"},
            'end_position': ('django.db.models.fields.FloatField', [], {'db_column': "'pk_fin'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Path']", 'db_column': "'troncon'"}),
            'start_position': ('django.db.models.fields.FloatField', [], {'db_column': "'pk_debut'"}),
            'topo_object': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.TopologyMixin']", 'db_column': "'evenement'"})
        },
        'core.topologymixin': {
            'Meta': {'object_name': 'TopologyMixin', 'db_table': "'evenements'"},
            'date_insert': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_update': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'supprime'"}),
            'geom': ('django.contrib.gis.db.models.fields.LineStringField', [], {'spatial_index': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interventions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['maintenance.Intervention']", 'symmetrical': 'False'}),
            'kind': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.TopologyMixinKind']"}),
            'length': ('django.db.models.fields.FloatField', [], {'db_column': "'longueur'"}),
            'offset': ('django.db.models.fields.IntegerField', [], {'db_column': "'decallage'"}),
            'troncons': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Path']", 'through': "orm['core.PathAggregation']", 'symmetrical': 'False'})
        },
        'core.topologymixinkind': {
            'Meta': {'object_name': 'TopologyMixinKind', 'db_table': "'type_evenements'"},
            'code': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'maintenance.contractor': {
            'Meta': {'object_name': 'Contractor', 'db_table': "'prestataires'"},
            'code': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'contractor': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']"})
        },
        'maintenance.funding': {
            'Meta': {'object_name': 'Funding', 'db_table': "'financement'"},
            'amount': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organism': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maintenance.Organism']"}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maintenance.Project']"}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']"})
        },
        'maintenance.intervention': {
            'Meta': {'object_name': 'Intervention', 'db_table': "'interventions'"},
            'area': ('django.db.models.fields.IntegerField', [], {}),
            'comment': ('django.db.models.fields.TextField', [], {}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'disorders': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'interventions'", 'symmetrical': 'False', 'to': "orm['maintenance.InterventionDisorder']"}),
            'height': ('django.db.models.fields.FloatField', [], {}),
            'heliport_cost': ('django.db.models.fields.FloatField', [], {}),
            'in_maintenance': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'insert_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'intervention_id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'jobs': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['maintenance.InterventionJob']", 'through': "orm['maintenance.ManDay']", 'symmetrical': 'False'}),
            'length': ('django.db.models.fields.FloatField', [], {}),
            'material_cost': ('django.db.models.fields.FloatField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maintenance.Project']", 'null': 'True', 'blank': 'True'}),
            'slope': ('django.db.models.fields.IntegerField', [], {}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maintenance.InterventionStatus']"}),
            'subcontract_cost': ('django.db.models.fields.FloatField', [], {}),
            'typology': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maintenance.InterventionTypology']", 'null': 'True', 'blank': 'True'}),
            'update_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'width': ('django.db.models.fields.FloatField', [], {})
        },
        'maintenance.interventiondisorder': {
            'Meta': {'object_name': 'InterventionDisorder', 'db_table': "'desordres'"},
            'code': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'disorder': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'disorder_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'disorder_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'disorder_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']"})
        },
        'maintenance.interventionjob': {
            'Meta': {'object_name': 'InterventionJob', 'db_table': "'bib_fonctions'"},
            'code': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'job': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']"})
        },
        'maintenance.interventionstatus': {
            'Meta': {'object_name': 'InterventionStatus', 'db_table': "'bib_de_suivi'"},
            'code': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'status_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'status_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'status_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']"})
        },
        'maintenance.interventiontypology': {
            'Meta': {'object_name': 'InterventionTypology', 'db_table': "'typologie_des_interventions'"},
            'code': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']"}),
            'typology': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'typology_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'typology_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'typology_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'})
        },
        'maintenance.manday': {
            'Meta': {'object_name': 'ManDay', 'db_table': "'journeeshomme'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intervention': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maintenance.Intervention']"}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maintenance.InterventionJob']"}),
            'nb_days': ('django.db.models.fields.IntegerField', [], {})
        },
        'maintenance.organism': {
            'Meta': {'object_name': 'Organism', 'db_table': "'liste_de_tous_les_organismes'"},
            'code': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'organism': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'maintenance.project': {
            'Meta': {'object_name': 'Project', 'db_table': "'chantiers'"},
            'begin_year': ('django.db.models.fields.IntegerField', [], {}),
            'comment': ('django.db.models.fields.TextField', [], {}),
            'constraint': ('django.db.models.fields.TextField', [], {}),
            'contractors': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'projects'", 'symmetrical': 'False', 'to': "orm['maintenance.Contractor']"}),
            'cost': ('django.db.models.fields.FloatField', [], {}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'end_year': ('django.db.models.fields.IntegerField', [], {}),
            'founders': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['maintenance.Organism']", 'through': "orm['maintenance.Funding']", 'symmetrical': 'False'}),
            'insert_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'project_id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'project_manager': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'manage'", 'to': "orm['maintenance.Organism']"}),
            'project_owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'own'", 'to': "orm['maintenance.Organism']"}),
            'update_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['core']
