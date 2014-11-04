# -*- coding: utf-8 -*-

from south.db import db
from south.v2 import SchemaMigration
from django.conf import settings
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TouristicContentType'
        db.create_table('t_b_contenu_touristique_type', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(related_name='types', db_column='categorie', to=orm['tourism.TouristicContentCategory'])),
            ('type_nr', self.gf('django.db.models.fields.IntegerField')(db_column='no_type')),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='nom')),
        ))
        db.send_create_signal(u'tourism', ['TouristicContentType'])

        # Adding M2M table for field type1 on 'TouristicContent'
        m2m_table_name = db.shorten_name('t_t_contenu_touristique_type1')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('touristiccontent', models.ForeignKey(orm[u'tourism.touristiccontent'], null=False)),
            ('touristiccontenttype', models.ForeignKey(orm[u'tourism.touristiccontenttype'], null=False))
        ))
        db.create_unique(m2m_table_name, ['touristiccontent_id', 'touristiccontenttype_id'])

        # Adding M2M table for field type2 on 'TouristicContent'
        m2m_table_name = db.shorten_name('t_t_contenu_touristique_type2')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('touristiccontent', models.ForeignKey(orm[u'tourism.touristiccontent'], null=False)),
            ('touristiccontenttype', models.ForeignKey(orm[u'tourism.touristiccontenttype'], null=False))
        ))
        db.create_unique(m2m_table_name, ['touristiccontent_id', 'touristiccontenttype_id'])

    def backwards(self, orm):
        # Deleting model 'TouristicContentType'
        db.delete_table('t_b_contenu_touristique_type')

        # Removing M2M table for field type1 on 'TouristicContent'
        db.delete_table(db.shorten_name('t_t_contenu_touristique_type1'))

        # Removing M2M table for field type2 on 'TouristicContent'
        db.delete_table(db.shorten_name('t_t_contenu_touristique_type2'))

    models = {
        u'authent.structure': {
            'Meta': {'ordering': "['name']", 'object_name': 'Structure'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'common.theme': {
            'Meta': {'ordering': "['label']", 'object_name': 'Theme', 'db_table': "'o_b_theme'"},
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
            'Meta': {'ordering': "['name']", 'object_name': 'InformationDesk', 'db_table': "'o_b_renseignement'"},
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
            'Meta': {'ordering': "['label']", 'object_name': 'InformationDeskType', 'db_table': "'o_b_type_renseignement'"},
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
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '256', 'null': 'True', 'db_column': "'email'", 'blank': 'True'}),
            'geom': ('django.contrib.gis.db.models.fields.GeometryField', [], {'srid': str(settings.SRID)}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'nom'"}),
            'practical_info': ('django.db.models.fields.TextField', [], {'db_column': "'infos_pratiques'", 'blank': 'True'}),
            'publication_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'db_column': "'date_publication'", 'blank': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'public'"}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['authent.Structure']", 'db_column': "'structure'"}),
            'themes': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'touristiccontents'", 'to': u"orm['common.Theme']", 'db_table': "'o_r_contenu_touristique_theme'", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'type1': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'contents1'", 'blank': 'True', 'db_column': "'type1'", 'to': u"orm['tourism.TouristicContentType']"}),
            'type2': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'contents2'", 'blank': 'True', 'db_column': "'type2'", 'to': u"orm['tourism.TouristicContentType']"}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '256', 'null': 'True', 'db_column': "'website'", 'blank': 'True'})
        },
        u'tourism.touristiccontentcategory': {
            'Meta': {'ordering': "['label']", 'object_name': 'TouristicContentCategory', 'db_table': "'t_b_contenu_touristique'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'nom'"}),
            'pictogram': ('django.db.models.fields.files.FileField', [], {'max_length': '512', 'null': 'True', 'db_column': "'picto'"})
        },
        u'tourism.touristiccontenttype': {
            'Meta': {'ordering': "['label']", 'object_name': 'TouristicContentType', 'db_table': "'t_b_contenu_touristique_type'"},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'types'", 'db_column': "'categorie'", 'to': u"orm['tourism.TouristicContentCategory']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'nom'"}),
            'type_nr': ('django.db.models.fields.IntegerField', [], {'db_column': "'no_type'"})
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
            'public': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tourism.TouristicEventPublic']", 'null': 'True', 'db_column': "'public_vise'", 'blank': 'True'}),
            'publication_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'db_column': "'date_publication'", 'blank': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'public'"}),
            'speaker': ('django.db.models.fields.CharField', [], {'max_length': '256', 'db_column': "'intervenant'", 'blank': 'True'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['authent.Structure']", 'db_column': "'structure'"}),
            'themes': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'touristic_events'", 'to': u"orm['common.Theme']", 'db_table': "'o_r_evenement_touristique_theme'", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'usage': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tourism.TouristicEventUsage']", 'null': 'True', 'db_column': "'usage'", 'blank': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '256', 'null': 'True', 'db_column': "'website'", 'blank': 'True'})
        },
        u'tourism.touristiceventpublic': {
            'Meta': {'ordering': "['public']", 'object_name': 'TouristicEventPublic', 'db_table': "'o_b_evenement_touristique_public'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'public': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'public'"})
        },
        u'tourism.touristiceventusage': {
            'Meta': {'ordering': "['usage']", 'object_name': 'TouristicEventUsage', 'db_table': "'o_b_evenement_touristique_usage'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'usage': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'usage'"})
        }
    }

    complete_apps = ['tourism']
