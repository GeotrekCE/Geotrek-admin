# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.conf import settings


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'TouristicContent.source'
        db.delete_column('t_t_contenu_touristique', 'source')

        # Adding M2M table for field source on 'TouristicContent'
        m2m_table_name = 't_r_contenu_touristique_source'
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('touristiccontent', models.ForeignKey(orm[u'tourism.touristiccontent'], null=False)),
            ('recordsource', models.ForeignKey(orm[u'common.recordsource'], null=False))
        ))
        db.create_unique(m2m_table_name, ['touristiccontent_id', 'recordsource_id'])

        # Deleting field 'TouristicEvent.source'
        db.delete_column('t_t_evenement_touristique', 'source')

        # Adding M2M table for field source on 'TouristicEvent'
        m2m_table_name = 't_r_evenement_touristique_source'
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('touristicevent', models.ForeignKey(orm[u'tourism.touristicevent'], null=False)),
            ('recordsource', models.ForeignKey(orm[u'common.recordsource'], null=False))
        ))
        db.create_unique(m2m_table_name, ['touristicevent_id', 'recordsource_id'])

    def backwards(self, orm):
        # Adding field 'TouristicContent.source'
        db.add_column('t_t_contenu_touristique', 'source',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='touristiccontents', null=True, to=orm['common.RecordSource'], db_column='source', blank=True),
                      keep_default=False)

        # Removing M2M table for field source on 'TouristicContent'
        db.delete_table('t_r_contenu_touristique_source')

        # Adding field 'TouristicEvent.source'
        db.add_column('t_t_evenement_touristique', 'source',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='touristicevents', null=True, to=orm['common.RecordSource'], db_column='source', blank=True),
                      keep_default=False)

        # Removing M2M table for field source on 'TouristicEvent'
        db.delete_table('t_r_evenement_touristique_source')

    models = {
        u'authent.structure': {
            'Meta': {'ordering': "['name']", 'object_name': 'Structure'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'cirkwi.cirkwitag': {
            'Meta': {'ordering': "['name']", 'object_name': 'CirkwiTag', 'db_table': "'o_b_cirkwi_tag'"},
            'eid': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'nom'"})
        },
        u'common.recordsource': {
            'Meta': {'ordering': "['name']", 'object_name': 'RecordSource', 'db_table': "'o_b_source_fiche'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'pictogram': ('django.db.models.fields.files.FileField', [], {'max_length': '512', 'null': 'True', 'db_column': "'picto'", 'blank': 'True'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['authent.Structure']", 'db_column': "'structure'"}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '256', 'null': 'True', 'db_column': "'website'", 'blank': 'True'})
        },
        u'common.theme': {
            'Meta': {'ordering': "['label']", 'object_name': 'Theme', 'db_table': "'o_b_theme'"},
            'cirkwi': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cirkwi.CirkwiTag']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'theme'"}),
            'pictogram': ('django.db.models.fields.files.FileField', [], {'max_length': '512', 'null': 'True', 'db_column': "'picto'"})
        },
        u'tourism.datasource': {
            'Meta': {'ordering': "['title', 'url']", 'object_name': 'DataSource', 'db_table': "'t_t_source_donnees'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pictogram': ('django.db.models.fields.files.FileField', [], {'max_length': '512', 'db_column': "'picto'"}),
            'targets': ('multiselectfield.db.fields.MultiSelectField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'titre'"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_column': "'type'"}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '400', 'db_column': "'url'"})
        },
        u'tourism.informationdesk': {
            'Meta': {'ordering': "['name']", 'object_name': 'InformationDesk', 'db_table': "'t_b_renseignement'"},
            'description': ('django.db.models.fields.TextField', [], {'db_column': "'description'", 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '256', 'null': 'True', 'db_column': "'email'", 'blank': 'True'}),
            'geom': ('django.contrib.gis.db.models.fields.PointField', [], {'srid': str(settings.SRID), 'null': 'True', 'spatial_index': 'False', 'db_column': "'geom'", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'municipality': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'db_column': "'commune'", 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'db_column': "'nom'"}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'db_column': "'telephone'", 'blank': 'True'}),
            'photo': ('django.db.models.fields.files.FileField', [], {'max_length': '512', 'null': 'True', 'db_column': "'photo'", 'blank': 'True'}),
            'postal_code': ('django.db.models.fields.CharField', [], {'max_length': '8', 'null': 'True', 'db_column': "'code'", 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'db_column': "'rue'", 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'desks'", 'db_column': "'type'", 'to': u"orm['tourism.InformationDeskType']"}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '256', 'null': 'True', 'db_column': "'website'", 'blank': 'True'})
        },
        u'tourism.informationdesktype': {
            'Meta': {'ordering': "['label']", 'object_name': 'InformationDeskType', 'db_table': "'t_b_type_renseignement'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'label'"}),
            'pictogram': ('django.db.models.fields.files.FileField', [], {'max_length': '512', 'null': 'True', 'db_column': "'picto'"})
        },
        u'tourism.touristiccontent': {
            'Meta': {'object_name': 'TouristicContent', 'db_table': "'t_t_contenu_touristique'"},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'contents'", 'db_column': "'categorie'", 'to': u"orm['tourism.TouristicContentCategory']"}),
            'contact': ('django.db.models.fields.TextField', [], {'db_column': "'contact'", 'blank': 'True'}),
            'date_insert': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_column': "'date_insert'", 'blank': 'True'}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_column': "'date_update'", 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'supprime'"}),
            'description': ('django.db.models.fields.TextField', [], {'db_column': "'description'", 'blank': 'True'}),
            'description_teaser': ('django.db.models.fields.TextField', [], {'db_column': "'chapeau'", 'blank': 'True'}),
            'eid': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'id_externe'", 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '256', 'null': 'True', 'db_column': "'email'", 'blank': 'True'}),
            'geom': ('django.contrib.gis.db.models.fields.GeometryField', [], {'srid': str(settings.SRID)}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'nom'"}),
            'practical_info': ('django.db.models.fields.TextField', [], {'db_column': "'infos_pratiques'", 'blank': 'True'}),
            'publication_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'db_column': "'date_publication'", 'blank': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'public'"}),
            'review': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'relecture'"}),
            'source': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'touristiccontents'", 'to': u"orm['common.RecordSource']", 'db_table': "'t_r_contenu_touristique_source'", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['authent.Structure']", 'db_column': "'structure'"}),
            'themes': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'touristiccontents'", 'to': u"orm['common.Theme']", 'db_table': "'t_r_contenu_touristique_theme'", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'type1': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'contents1'", 'blank': 'True', 'db_table': "'t_r_contenu_touristique_type1'", 'to': u"orm['tourism.TouristicContentType']"}),
            'type2': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'contents2'", 'blank': 'True', 'db_table': "'t_r_contenu_touristique_type2'", 'to': u"orm['tourism.TouristicContentType']"}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '256', 'null': 'True', 'db_column': "'website'", 'blank': 'True'})
        },
        u'tourism.touristiccontentcategory': {
            'Meta': {'ordering': "['label']", 'object_name': 'TouristicContentCategory', 'db_table': "'t_b_contenu_touristique_categorie'"},
            'geometry_type': ('django.db.models.fields.CharField', [], {'default': "'point'", 'max_length': '16', 'db_column': "'type_geometrie'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'nom'"}),
            'pictogram': ('django.db.models.fields.files.FileField', [], {'max_length': '512', 'null': 'True', 'db_column': "'picto'"}),
            'type1_label': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'label_type1'", 'blank': 'True'}),
            'type2_label': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'label_type2'", 'blank': 'True'})
        },
        u'tourism.touristiccontenttype': {
            'Meta': {'ordering': "['label']", 'object_name': 'TouristicContentType', 'db_table': "'t_b_contenu_touristique_type'"},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'types'", 'db_column': "'categorie'", 'to': u"orm['tourism.TouristicContentCategory']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_list': ('django.db.models.fields.IntegerField', [], {'db_column': "'liste_choix'"}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'nom'"}),
            'pictogram': ('django.db.models.fields.files.FileField', [], {'max_length': '512', 'null': 'True', 'db_column': "'picto'", 'blank': 'True'})
        },
        u'tourism.touristicevent': {
            'Meta': {'ordering': "['-begin_date']", 'object_name': 'TouristicEvent', 'db_table': "'t_t_evenement_touristique'"},
            'accessibility': ('django.db.models.fields.CharField', [], {'max_length': '256', 'db_column': "'accessibilite'", 'blank': 'True'}),
            'begin_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'db_column': "'date_debut'", 'blank': 'True'}),
            'booking': ('django.db.models.fields.TextField', [], {'db_column': "'reservation'", 'blank': 'True'}),
            'contact': ('django.db.models.fields.TextField', [], {'db_column': "'contact'", 'blank': 'True'}),
            'date_insert': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_column': "'date_insert'", 'blank': 'True'}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_column': "'date_update'", 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'supprime'"}),
            'description': ('django.db.models.fields.TextField', [], {'db_column': "'description'", 'blank': 'True'}),
            'description_teaser': ('django.db.models.fields.TextField', [], {'db_column': "'chapeau'", 'blank': 'True'}),
            'duration': ('django.db.models.fields.CharField', [], {'max_length': '64', 'db_column': "'duree'", 'blank': 'True'}),
            'eid': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'id_externe'", 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '256', 'null': 'True', 'db_column': "'email'", 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'db_column': "'date_fin'", 'blank': 'True'}),
            'geom': ('django.contrib.gis.db.models.fields.PointField', [], {'srid': str(settings.SRID)}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meeting_point': ('django.db.models.fields.CharField', [], {'max_length': '256', 'db_column': "'point_rdv'", 'blank': 'True'}),
            'meeting_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'db_column': "'heure_rdv'", 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'nom'"}),
            'organizer': ('django.db.models.fields.CharField', [], {'max_length': '256', 'db_column': "'organisateur'", 'blank': 'True'}),
            'participant_number': ('django.db.models.fields.CharField', [], {'max_length': '256', 'db_column': "'nb_places'", 'blank': 'True'}),
            'practical_info': ('django.db.models.fields.TextField', [], {'db_column': "'infos_pratiques'", 'blank': 'True'}),
            'publication_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'db_column': "'date_publication'", 'blank': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'public'"}),
            'review': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'relecture'"}),
            'source': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'touristicevents'", 'to': u"orm['common.RecordSource']", 'db_table': "'t_r_evenement_touristique_source'", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'speaker': ('django.db.models.fields.CharField', [], {'max_length': '256', 'db_column': "'intervenant'", 'blank': 'True'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['authent.Structure']", 'db_column': "'structure'"}),
            'target_audience': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'public_vise'", 'blank': 'True'}),
            'themes': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'touristic_events'", 'to': u"orm['common.Theme']", 'db_table': "'t_r_evenement_touristique_theme'", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tourism.TouristicEventType']", 'null': 'True', 'db_column': "'type'", 'blank': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '256', 'null': 'True', 'db_column': "'website'", 'blank': 'True'})
        },
        u'tourism.touristiceventtype': {
            'Meta': {'ordering': "['type']", 'object_name': 'TouristicEventType', 'db_table': "'t_b_evenement_touristique_type'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pictogram': ('django.db.models.fields.files.FileField', [], {'max_length': '512', 'null': 'True', 'db_column': "'picto'", 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'type'"})
        }
    }

    complete_apps = ['tourism']
