# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.conf import settings


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Renaming column for 'Trek.is_park_centered' to match new field type.
        db.rename_column('o_t_itineraire', 'is_park_centered', 'coeur')
        # Changing field 'Trek.is_park_centered'
        db.alter_column('o_t_itineraire', 'coeur', self.gf('django.db.models.fields.BooleanField')(db_column='coeur'))

        # Renaming column for 'Trek.name_fr' to match new field type.
        db.rename_column('o_t_itineraire', 'name_fr', 'nom_fr')
        # Changing field 'Trek.name_fr'
        db.alter_column('o_t_itineraire', 'nom_fr', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, db_column='nom'))

        # Renaming column for 'Trek.description_teaser_fr' to match new field type.
        db.rename_column('o_t_itineraire', 'description_teaser_fr', 'chapeau_fr')
        # Changing field 'Trek.description_teaser_fr'
        db.alter_column('o_t_itineraire', 'chapeau_fr', self.gf('django.db.models.fields.TextField')(null=True, db_column='chapeau'))

        # Changing field 'Trek.ambiance'
        db.alter_column('o_t_itineraire', 'ambiance', self.gf('django.db.models.fields.TextField')(db_column='ambiance'))

        # Changing field 'Trek.ambiance_it'
        db.alter_column('o_t_itineraire', 'ambiance_it', self.gf('django.db.models.fields.TextField')(null=True, db_column='ambiance'))

        # Renaming column for 'Trek.access_en' to match new field type.
        db.rename_column('o_t_itineraire', 'access_en', 'acces_en')
        # Changing field 'Trek.access_en'
        db.alter_column('o_t_itineraire', 'acces_en', self.gf('django.db.models.fields.TextField')(null=True, db_column='acces'))

        # Renaming column for 'Trek.arrival_en' to match new field type.
        db.rename_column('o_t_itineraire', 'arrival_en', 'arrivee_en')
        # Changing field 'Trek.arrival_en'
        db.alter_column('o_t_itineraire', 'arrivee_en', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, db_column='arrivee'))

        # Renaming column for 'Trek.departure_en' to match new field type.
        db.rename_column('o_t_itineraire', 'departure_en', 'depart_en')
        # Changing field 'Trek.departure_en'
        db.alter_column('o_t_itineraire', 'depart_en', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, db_column='depart'))

        # Changing field 'Trek.description_fr'
        db.alter_column('o_t_itineraire', 'description_fr', self.gf('django.db.models.fields.TextField')(null=True, db_column='description'))

        # Renaming column for 'Trek.duration' to match new field type.
        db.rename_column('o_t_itineraire', 'duration', 'duree')
        # Changing field 'Trek.duration'
        db.alter_column('o_t_itineraire', 'duree', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='duree'))

        # Renaming column for 'Trek.arrival_it' to match new field type.
        db.rename_column('o_t_itineraire', 'arrival_it', 'arrivee_it')
        # Changing field 'Trek.arrival_it'
        db.alter_column('o_t_itineraire', 'arrivee_it', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, db_column='arrivee'))

        # Renaming column for 'Trek.name_en' to match new field type.
        db.rename_column('o_t_itineraire', 'name_en', 'nom_en')
        # Changing field 'Trek.name_en'
        db.alter_column('o_t_itineraire', 'nom_en', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, db_column='nom'))

        # Renaming column for 'Trek.name_it' to match new field type.
        db.rename_column('o_t_itineraire', 'name_it', 'nom_it')
        # Changing field 'Trek.name_it'
        db.alter_column('o_t_itineraire', 'nom_it', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, db_column='nom'))

        # Renaming column for 'Trek.departure_it' to match new field type.
        db.rename_column('o_t_itineraire', 'departure_it', 'depart_it')
        # Changing field 'Trek.departure_it'
        db.alter_column('o_t_itineraire', 'depart_it', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, db_column='depart'))

        # Renaming column for 'Trek.parking_location' to match new field type.
        db.rename_column('o_t_itineraire', 'parking_location', 'geom_parking')
        # Changing field 'Trek.parking_location'
        db.alter_column('o_t_itineraire', 'geom_parking', self.gf('django.contrib.gis.db.models.fields.PointField')(srid=settings.SRID, null=True, spatial_index=False, db_column='geom_parking'))

        # Renaming column for 'Trek.description_teaser' to match new field type.
        db.rename_column('o_t_itineraire', 'description_teaser', 'chapeau')
        # Changing field 'Trek.description_teaser'
        db.alter_column('o_t_itineraire', 'chapeau', self.gf('django.db.models.fields.TextField')(db_column='chapeau'))

        # Renaming column for 'Trek.access' to match new field type.
        db.rename_column('o_t_itineraire', 'access', 'acces')
        # Changing field 'Trek.access'
        db.alter_column('o_t_itineraire', 'acces', self.gf('django.db.models.fields.TextField')(db_column='acces'))

        # Renaming column for 'Trek.advice_it' to match new field type.
        db.rename_column('o_t_itineraire', 'advice_it', 'recommandation_it')
        # Changing field 'Trek.advice_it'
        db.alter_column('o_t_itineraire', 'recommandation_it', self.gf('django.db.models.fields.TextField')(null=True, db_column='recommandation'))

        # Renaming column for 'Trek.description_teaser_it' to match new field type.
        db.rename_column('o_t_itineraire', 'description_teaser_it', 'chapeau_it')
        # Changing field 'Trek.description_teaser_it'
        db.alter_column('o_t_itineraire', 'chapeau_it', self.gf('django.db.models.fields.TextField')(null=True, db_column='chapeau'))

        # Renaming column for 'Trek.arrival' to match new field type.
        db.rename_column('o_t_itineraire', 'arrival', 'arrivee')
        # Changing field 'Trek.arrival'
        db.alter_column('o_t_itineraire', 'arrivee', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='arrivee'))

        # Renaming column for 'Trek.departure_fr' to match new field type.
        db.rename_column('o_t_itineraire', 'departure_fr', 'depart_fr')
        # Changing field 'Trek.departure_fr'
        db.alter_column('o_t_itineraire', 'depart_fr', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, db_column='depart'))

        # Changing field 'Trek.description'
        db.alter_column('o_t_itineraire', 'description', self.gf('django.db.models.fields.TextField')(db_column='description'))

        # Renaming column for 'Trek.access_fr' to match new field type.
        db.rename_column('o_t_itineraire', 'access_fr', 'acces_fr')
        # Changing field 'Trek.access_fr'
        db.alter_column('o_t_itineraire', 'acces_fr', self.gf('django.db.models.fields.TextField')(null=True, db_column='acces'))

        # Renaming column for 'Trek.advice' to match new field type.
        db.rename_column('o_t_itineraire', 'advice', 'recommandation')
        # Changing field 'Trek.advice'
        db.alter_column('o_t_itineraire', 'recommandation', self.gf('django.db.models.fields.TextField')(db_column='recommandation'))

        # Renaming column for 'Trek.disabled_infrastructure' to match new field type.
        db.rename_column('o_t_itineraire', 'disabled_infrastructure', 'handicap')
        # Changing field 'Trek.disabled_infrastructure'
        db.alter_column('o_t_itineraire', 'handicap', self.gf('django.db.models.fields.TextField')(db_column='handicap'))

        # Changing field 'Trek.description_en'
        db.alter_column('o_t_itineraire', 'description_en', self.gf('django.db.models.fields.TextField')(null=True, db_column='description'))

        # Renaming column for 'Trek.description_teaser_en' to match new field type.
        db.rename_column('o_t_itineraire', 'description_teaser_en', 'chapeau_en')
        # Changing field 'Trek.description_teaser_en'
        db.alter_column('o_t_itineraire', 'chapeau_en', self.gf('django.db.models.fields.TextField')(null=True, db_column='chapeau'))

        # Renaming column for 'Trek.difficulty' to match new field type.
        db.rename_column('o_t_itineraire', 'difficulty_id', 'difficulte')
        # Changing field 'Trek.difficulty'
        db.alter_column('o_t_itineraire', 'difficulte', self.gf('django.db.models.fields.related.ForeignKey')(null=True, db_column='difficulte', to=orm['trekking.DifficultyLevel']))

        # Renaming column for 'Trek.disabled_infrastructure_fr' to match new field type.
        db.rename_column('o_t_itineraire', 'disabled_infrastructure_fr', 'handicap_fr')
        # Changing field 'Trek.disabled_infrastructure_fr'
        db.alter_column('o_t_itineraire', 'handicap_fr', self.gf('django.db.models.fields.TextField')(null=True, db_column='handicap'))

        # Changing field 'Trek.description_it'
        db.alter_column('o_t_itineraire', 'description_it', self.gf('django.db.models.fields.TextField')(null=True, db_column='description'))

        # Changing field 'Trek.ambiance_fr'
        db.alter_column('o_t_itineraire', 'ambiance_fr', self.gf('django.db.models.fields.TextField')(null=True, db_column='ambiance'))

        # Renaming column for 'Trek.advised_parking' to match new field type.
        db.rename_column('o_t_itineraire', 'advised_parking', 'parking')
        # Changing field 'Trek.advised_parking'
        db.alter_column('o_t_itineraire', 'parking', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='parking'))

        # Renaming column for 'Trek.advice_en' to match new field type.
        db.rename_column('o_t_itineraire', 'advice_en', 'recommandation_en')
        # Changing field 'Trek.advice_en'
        db.alter_column('o_t_itineraire', 'recommandation_en', self.gf('django.db.models.fields.TextField')(null=True, db_column='recommandation'))

        # Renaming column for 'Trek.name' to match new field type.
        db.rename_column('o_t_itineraire', 'name', 'nom')
        # Changing field 'Trek.name'
        db.alter_column('o_t_itineraire', 'nom', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='nom'))

        # Renaming column for 'Trek.disabled_infrastructure_it' to match new field type.
        db.rename_column('o_t_itineraire', 'disabled_infrastructure_it', 'handicap_it')
        # Changing field 'Trek.disabled_infrastructure_it'
        db.alter_column('o_t_itineraire', 'handicap_it', self.gf('django.db.models.fields.TextField')(null=True, db_column='handicap'))

        # Renaming column for 'Trek.arrival_fr' to match new field type.
        db.rename_column('o_t_itineraire', 'arrival_fr', 'arrivee_fr')
        # Changing field 'Trek.arrival_fr'
        db.alter_column('o_t_itineraire', 'arrivee_fr', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, db_column='arrivee'))

        # Renaming column for 'Trek.access_it' to match new field type.
        db.rename_column('o_t_itineraire', 'access_it', 'acces_it')
        # Changing field 'Trek.access_it'
        db.alter_column('o_t_itineraire', 'acces_it', self.gf('django.db.models.fields.TextField')(null=True, db_column='acces'))

        # Renaming column for 'Trek.route' to match new field type.
        db.rename_column('o_t_itineraire', 'route_id', 'parcours')
        # Changing field 'Trek.route'
        db.alter_column('o_t_itineraire', 'parcours', self.gf('django.db.models.fields.related.ForeignKey')(null=True, db_column='parcours', to=orm['trekking.Route']))

        # Renaming column for 'Trek.departure' to match new field type.
        db.rename_column('o_t_itineraire', 'departure', 'depart')
        # Changing field 'Trek.departure'
        db.alter_column('o_t_itineraire', 'depart', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='depart'))

        # Changing field 'Trek.ambiance_en'
        db.alter_column('o_t_itineraire', 'ambiance_en', self.gf('django.db.models.fields.TextField')(null=True, db_column='ambiance'))

        # Renaming column for 'Trek.public_transport' to match new field type.
        db.rename_column('o_t_itineraire', 'public_transport', 'transport')
        # Changing field 'Trek.public_transport'
        db.alter_column('o_t_itineraire', 'transport', self.gf('django.db.models.fields.TextField')(db_column='transport'))

        # Renaming column for 'Trek.disabled_infrastructure_en' to match new field type.
        db.rename_column('o_t_itineraire', 'disabled_infrastructure_en', 'handicap_en')
        # Changing field 'Trek.disabled_infrastructure_en'
        db.alter_column('o_t_itineraire', 'handicap_en', self.gf('django.db.models.fields.TextField')(null=True, db_column='handicap'))

        # Renaming column for 'Trek.published' to match new field type.
        db.rename_column('o_t_itineraire', 'published', 'public')
        # Changing field 'Trek.published'
        db.alter_column('o_t_itineraire', 'public', self.gf('django.db.models.fields.BooleanField')(db_column='public'))

        # Renaming column for 'Trek.advice_fr' to match new field type.
        db.rename_column('o_t_itineraire', 'advice_fr', 'recommandation_fr')
        # Changing field 'Trek.advice_fr'
        db.alter_column('o_t_itineraire', 'recommandation_fr', self.gf('django.db.models.fields.TextField')(null=True, db_column='recommandation'))

        # Renaming column for 'TrekNetwork.network_it' to match new field type.
        db.rename_column('o_b_reseau', 'network_it', 'reseau_it')
        # Changing field 'TrekNetwork.network_it'
        db.alter_column('o_b_reseau', 'reseau_it', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, db_column='reseau'))

        # Renaming column for 'TrekNetwork.network' to match new field type.
        db.rename_column('o_b_reseau', 'network', 'reseau')
        # Changing field 'TrekNetwork.network'
        db.alter_column('o_b_reseau', 'reseau', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='reseau'))

        # Renaming column for 'TrekNetwork.network_en' to match new field type.
        db.rename_column('o_b_reseau', 'network_en', 'reseau_en')
        # Changing field 'TrekNetwork.network_en'
        db.alter_column('o_b_reseau', 'reseau_en', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, db_column='reseau'))

        # Renaming column for 'TrekNetwork.network_fr' to match new field type.
        db.rename_column('o_b_reseau', 'network_fr', 'reseau_fr')
        # Changing field 'TrekNetwork.network_fr'
        db.alter_column('o_b_reseau', 'reseau_fr', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, db_column='reseau'))

        # Changing field 'Usage.usage_fr'
        db.alter_column('o_b_usage', 'usage_fr', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, db_column='usage'))

        # Renaming column for 'Usage.pictogram' to match new field type.
        db.rename_column('o_b_usage', 'pictogram', 'picto')
        # Changing field 'Usage.pictogram'
        db.alter_column('o_b_usage', 'picto', self.gf('django.db.models.fields.files.FileField')(max_length=100, db_column='picto'))

        # Changing field 'Usage.usage_it'
        db.alter_column('o_b_usage', 'usage_it', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, db_column='usage'))

        # Changing field 'Usage.usage_en'
        db.alter_column('o_b_usage', 'usage_en', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, db_column='usage'))

        # Changing field 'Usage.usage'
        db.alter_column('o_b_usage', 'usage', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='usage'))

        # Renaming column for 'WebLink.category' to match new field type.
        db.rename_column('o_t_web', 'category_id', 'categorie')
        # Changing field 'WebLink.category'
        db.alter_column('o_t_web', 'categorie', self.gf('django.db.models.fields.related.ForeignKey')(null=True, db_column='categorie', to=orm['trekking.WebLinkCategory']))

        # Renaming column for 'WebLink.name_fr' to match new field type.
        db.rename_column('o_t_web', 'name_fr', 'nom_fr')
        # Changing field 'WebLink.name_fr'
        db.alter_column('o_t_web', 'nom_fr', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, db_column='nom'))

        # Renaming column for 'WebLink.name_it' to match new field type.
        db.rename_column('o_t_web', 'name_it', 'nom_it')
        # Changing field 'WebLink.name_it'
        db.alter_column('o_t_web', 'nom_it', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, db_column='nom'))

        # Renaming column for 'WebLink.name' to match new field type.
        db.rename_column('o_t_web', 'name', 'nom')
        # Changing field 'WebLink.name'
        db.alter_column('o_t_web', 'nom', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='nom'))

        # Changing field 'WebLink.url'
        db.alter_column('o_t_web', 'url', self.gf('django.db.models.fields.URLField')(max_length=128, db_column='url'))

        # Renaming column for 'WebLink.name_en' to match new field type.
        db.rename_column('o_t_web', 'name_en', 'nom_en')
        # Changing field 'WebLink.name_en'
        db.alter_column('o_t_web', 'nom_en', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, db_column='nom'))

        # Renaming column for 'TrekRelationship.trek_a' to match new field type.
        db.rename_column('o_r_itineraire_itineraire', 'trek_a_id', 'itineraire_a')
        # Changing field 'TrekRelationship.trek_a'
        db.alter_column('o_r_itineraire_itineraire', 'itineraire_a', self.gf('django.db.models.fields.related.ForeignKey')(db_column='itineraire_a', to=orm['trekking.Trek']))

        # Renaming column for 'TrekRelationship.trek_b' to match new field type.
        db.rename_column('o_r_itineraire_itineraire', 'trek_b_id', 'itineraire_b')
        # Changing field 'TrekRelationship.trek_b'
        db.alter_column('o_r_itineraire_itineraire', 'itineraire_b', self.gf('django.db.models.fields.related.ForeignKey')(db_column='itineraire_b', to=orm['trekking.Trek']))

        # Renaming column for 'TrekRelationship.has_common_departure' to match new field type.
        db.rename_column('o_r_itineraire_itineraire', 'has_common_departure', 'depart_commun')
        # Changing field 'TrekRelationship.has_common_departure'
        db.alter_column('o_r_itineraire_itineraire', 'depart_commun', self.gf('django.db.models.fields.BooleanField')(db_column='depart_commun'))

        # Renaming column for 'TrekRelationship.is_circuit_step' to match new field type.
        db.rename_column('o_r_itineraire_itineraire', 'is_circuit_step', 'etape_circuit')
        # Changing field 'TrekRelationship.is_circuit_step'
        db.alter_column('o_r_itineraire_itineraire', 'etape_circuit', self.gf('django.db.models.fields.BooleanField')(db_column='etape_circuit'))

        # Renaming column for 'TrekRelationship.has_common_edge' to match new field type.
        db.rename_column('o_r_itineraire_itineraire', 'has_common_edge', 'troncons_communs')
        # Changing field 'TrekRelationship.has_common_edge'
        db.alter_column('o_r_itineraire_itineraire', 'troncons_communs', self.gf('django.db.models.fields.BooleanField')(db_column='troncons_communs'))

        # Renaming column for 'Route.route_it' to match new field type.
        db.rename_column('o_b_parcours', 'route_it', 'parcours_it')
        # Changing field 'Route.route_it'
        db.alter_column('o_b_parcours', 'parcours_it', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, db_column='parcours'))

        # Renaming column for 'Route.route_fr' to match new field type.
        db.rename_column('o_b_parcours', 'route_fr', 'parcours_fr')
        # Changing field 'Route.route_fr'
        db.alter_column('o_b_parcours', 'parcours_fr', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, db_column='parcours'))

        # Renaming column for 'Route.route_en' to match new field type.
        db.rename_column('o_b_parcours', 'route_en', 'parcours_en')
        # Changing field 'Route.route_en'
        db.alter_column('o_b_parcours', 'parcours_en', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, db_column='parcours'))

        # Renaming column for 'Route.route' to match new field type.
        db.rename_column('o_b_parcours', 'route', 'parcours')
        # Changing field 'Route.route'
        db.alter_column('o_b_parcours', 'parcours', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='parcours'))

        # Renaming column for 'Theme.label_it' to match new field type.
        db.rename_column('o_b_theme', 'label_it', 'theme_it')
        # Changing field 'Theme.label_it'
        db.alter_column('o_b_theme', 'theme_it', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, db_column='theme'))

        # Renaming column for 'Theme.pictogram' to match new field type.
        db.rename_column('o_b_theme', 'pictogram', 'picto')
        # Changing field 'Theme.pictogram'
        db.alter_column('o_b_theme', 'picto', self.gf('django.db.models.fields.files.FileField')(max_length=100, db_column='picto'))

        # Renaming column for 'Theme.label' to match new field type.
        db.rename_column('o_b_theme', 'label', 'theme')
        # Changing field 'Theme.label'
        db.alter_column('o_b_theme', 'theme', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='theme'))

        # Renaming column for 'Theme.label_en' to match new field type.
        db.rename_column('o_b_theme', 'label_en', 'theme_en')
        # Changing field 'Theme.label_en'
        db.alter_column('o_b_theme', 'theme_en', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, db_column='theme'))

        # Renaming column for 'Theme.label_fr' to match new field type.
        db.rename_column('o_b_theme', 'label_fr', 'theme_fr')
        # Changing field 'Theme.label_fr'
        db.alter_column('o_b_theme', 'theme_fr', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, db_column='theme'))

        # Renaming column for 'DifficultyLevel.difficulty_it' to match new field type.
        db.rename_column('o_b_difficulte', 'difficulty_it', 'difficulte_it')
        # Changing field 'DifficultyLevel.difficulty_it'
        db.alter_column('o_b_difficulte', 'difficulte_it', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, db_column='difficulte'))

        # Renaming column for 'DifficultyLevel.difficulty' to match new field type.
        db.rename_column('o_b_difficulte', 'difficulty', 'difficulte')
        # Changing field 'DifficultyLevel.difficulty'
        db.alter_column('o_b_difficulte', 'difficulte', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='difficulte'))

        # Renaming column for 'DifficultyLevel.difficulty_fr' to match new field type.
        db.rename_column('o_b_difficulte', 'difficulty_fr', 'difficulte_fr')
        # Changing field 'DifficultyLevel.difficulty_fr'
        db.alter_column('o_b_difficulte', 'difficulte_fr', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, db_column='difficulte'))

        # Renaming column for 'DifficultyLevel.difficulty_en' to match new field type.
        db.rename_column('o_b_difficulte', 'difficulty_en', 'difficulte_en')
        # Changing field 'DifficultyLevel.difficulty_en'
        db.alter_column('o_b_difficulte', 'difficulte_en', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, db_column='difficulte'))

        # Renaming column for 'WebLinkCategory.label_it' to match new field type.
        db.rename_column('o_b_web_category', 'label_it', 'nom_it')
        # Changing field 'WebLinkCategory.label_it'
        db.alter_column('o_b_web_category', 'nom_it', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, db_column='nom'))

        # Renaming column for 'WebLinkCategory.pictogram' to match new field type.
        db.rename_column('o_b_web_category', 'pictogram', 'picto')
        # Changing field 'WebLinkCategory.pictogram'
        db.alter_column('o_b_web_category', 'picto', self.gf('django.db.models.fields.files.FileField')(max_length=100, db_column='picto'))

        # Renaming column for 'WebLinkCategory.label' to match new field type.
        db.rename_column('o_b_web_category', 'label', 'nom')
        # Changing field 'WebLinkCategory.label'
        db.alter_column('o_b_web_category', 'nom', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='nom'))

        # Renaming column for 'WebLinkCategory.label_en' to match new field type.
        db.rename_column('o_b_web_category', 'label_en', 'nom_en')
        # Changing field 'WebLinkCategory.label_en'
        db.alter_column('o_b_web_category', 'nom_en', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, db_column='nom'))

        # Renaming column for 'WebLinkCategory.label_fr' to match new field type.
        db.rename_column('o_b_web_category', 'label_fr', 'nom_fr')
        # Changing field 'WebLinkCategory.label_fr'
        db.alter_column('o_b_web_category', 'nom_fr', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, db_column='nom'))

        # Renaming column for 'POI.name_fr' to match new field type.
        db.rename_column('o_t_poi', 'name_fr', 'nom_fr')
        # Changing field 'POI.name_fr'
        db.alter_column('o_t_poi', 'nom_fr', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, db_column='nom'))

        # Renaming column for 'POI.name_it' to match new field type.
        db.rename_column('o_t_poi', 'name_it', 'nom_it')
        # Changing field 'POI.name_it'
        db.alter_column('o_t_poi', 'nom_it', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, db_column='nom'))

        # Renaming column for 'POI.name' to match new field type.
        db.rename_column('o_t_poi', 'name', 'nom')
        # Changing field 'POI.name'
        db.alter_column('o_t_poi', 'nom', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='nom'))

        # Changing field 'POI.description_en'
        db.alter_column('o_t_poi', 'description_en', self.gf('django.db.models.fields.TextField')(null=True, db_column='description'))

        # Changing field 'POI.description_fr'
        db.alter_column('o_t_poi', 'description_fr', self.gf('django.db.models.fields.TextField')(null=True, db_column='description'))

        # Changing field 'POI.description_it'
        db.alter_column('o_t_poi', 'description_it', self.gf('django.db.models.fields.TextField')(null=True, db_column='description'))

        # Renaming column for 'POI.name_en' to match new field type.
        db.rename_column('o_t_poi', 'name_en', 'nom_en')
        # Changing field 'POI.name_en'
        db.alter_column('o_t_poi', 'nom_en', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, db_column='nom'))

        # Renaming column for 'POI.type' to match new field type.
        db.rename_column('o_t_poi', 'type_id', 'type')
        # Changing field 'POI.type'
        db.alter_column('o_t_poi', 'type', self.gf('django.db.models.fields.related.ForeignKey')(db_column='type', to=orm['trekking.POIType']))

        # Changing field 'POI.description'
        db.alter_column('o_t_poi', 'description', self.gf('django.db.models.fields.TextField')(db_column='description'))

        # Renaming column for 'POIType.label_it' to match new field type.
        db.rename_column('o_b_poi', 'label_it', 'nom_it')
        # Changing field 'POIType.label_it'
        db.alter_column('o_b_poi', 'nom_it', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, db_column='nom'))

        # Renaming column for 'POIType.pictogram' to match new field type.
        db.rename_column('o_b_poi', 'pictogram', 'picto')
        # Changing field 'POIType.pictogram'
        db.alter_column('o_b_poi', 'picto', self.gf('django.db.models.fields.files.FileField')(max_length=100, db_column='picto'))

        # Renaming column for 'POIType.label' to match new field type.
        db.rename_column('o_b_poi', 'label', 'nom')
        # Changing field 'POIType.label'
        db.alter_column('o_b_poi', 'nom', self.gf('django.db.models.fields.CharField')(max_length=128, db_column='nom'))

        # Renaming column for 'POIType.label_en' to match new field type.
        db.rename_column('o_b_poi', 'label_en', 'nom_en')
        # Changing field 'POIType.label_en'
        db.alter_column('o_b_poi', 'nom_en', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, db_column='nom'))

        # Renaming column for 'POIType.label_fr' to match new field type.
        db.rename_column('o_b_poi', 'label_fr', 'nom_fr')
        # Changing field 'POIType.label_fr'
        db.alter_column('o_b_poi', 'nom_fr', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, db_column='nom'))

    def backwards(self, orm):

        # Renaming column for 'Trek.is_park_centered' to match new field type.
        db.rename_column('o_t_itineraire', 'coeur', 'is_park_centered')
        # Changing field 'Trek.is_park_centered'
        db.alter_column('o_t_itineraire', 'is_park_centered', self.gf('django.db.models.fields.BooleanField')())

        # Renaming column for 'Trek.name_fr' to match new field type.
        db.rename_column('o_t_itineraire', 'nom_fr', 'name_fr')
        # Changing field 'Trek.name_fr'
        db.alter_column('o_t_itineraire', 'name_fr', self.gf('django.db.models.fields.CharField')(max_length=128, null=True))

        # Renaming column for 'Trek.description_teaser_fr' to match new field type.
        db.rename_column('o_t_itineraire', 'chapeau_fr', 'description_teaser_fr')
        # Changing field 'Trek.description_teaser_fr'
        db.alter_column('o_t_itineraire', 'description_teaser_fr', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Trek.ambiance'
        db.alter_column('o_t_itineraire', 'ambiance', self.gf('django.db.models.fields.TextField')())

        # Changing field 'Trek.ambiance_it'
        db.alter_column('o_t_itineraire', 'ambiance_it', self.gf('django.db.models.fields.TextField')(null=True))

        # Renaming column for 'Trek.access_en' to match new field type.
        db.rename_column('o_t_itineraire', 'acces_en', 'access_en')
        # Changing field 'Trek.access_en'
        db.alter_column('o_t_itineraire', 'access_en', self.gf('django.db.models.fields.TextField')(null=True))

        # Renaming column for 'Trek.arrival_en' to match new field type.
        db.rename_column('o_t_itineraire', 'arrivee_en', 'arrival_en')
        # Changing field 'Trek.arrival_en'
        db.alter_column('o_t_itineraire', 'arrival_en', self.gf('django.db.models.fields.CharField')(max_length=128, null=True))

        # Renaming column for 'Trek.departure_en' to match new field type.
        db.rename_column('o_t_itineraire', 'depart_en', 'departure_en')
        # Changing field 'Trek.departure_en'
        db.alter_column('o_t_itineraire', 'departure_en', self.gf('django.db.models.fields.CharField')(max_length=128, null=True))

        # Changing field 'Trek.description_fr'
        db.alter_column('o_t_itineraire', 'description_fr', self.gf('django.db.models.fields.TextField')(null=True))

        # Renaming column for 'Trek.duration' to match new field type.
        db.rename_column('o_t_itineraire', 'duree', 'duration')
        # Changing field 'Trek.duration'
        db.alter_column('o_t_itineraire', 'duration', self.gf('django.db.models.fields.IntegerField')(null=True))

        # Renaming column for 'Trek.arrival_it' to match new field type.
        db.rename_column('o_t_itineraire', 'arrivee_it', 'arrival_it')
        # Changing field 'Trek.arrival_it'
        db.alter_column('o_t_itineraire', 'arrival_it', self.gf('django.db.models.fields.CharField')(max_length=128, null=True))

        # Renaming column for 'Trek.name_en' to match new field type.
        db.rename_column('o_t_itineraire', 'nom_en', 'name_en')
        # Changing field 'Trek.name_en'
        db.alter_column('o_t_itineraire', 'name_en', self.gf('django.db.models.fields.CharField')(max_length=128, null=True))

        # Renaming column for 'Trek.name_it' to match new field type.
        db.rename_column('o_t_itineraire', 'nom_it', 'name_it')
        # Changing field 'Trek.name_it'
        db.alter_column('o_t_itineraire', 'name_it', self.gf('django.db.models.fields.CharField')(max_length=128, null=True))

        # Renaming column for 'Trek.departure_it' to match new field type.
        db.rename_column('o_t_itineraire', 'depart_it', 'departure_it')
        # Changing field 'Trek.departure_it'
        db.alter_column('o_t_itineraire', 'departure_it', self.gf('django.db.models.fields.CharField')(max_length=128, null=True))

        # Renaming column for 'Trek.parking_location' to match new field type.
        db.rename_column('o_t_itineraire', 'geom_parking', 'parking_location')
        # Changing field 'Trek.parking_location'
        db.alter_column('o_t_itineraire', 'parking_location', self.gf('django.contrib.gis.db.models.fields.PointField')(srid=settings.SRID, null=True, spatial_index=False))

        # Renaming column for 'Trek.description_teaser' to match new field type.
        db.rename_column('o_t_itineraire', 'chapeau', 'description_teaser')
        # Changing field 'Trek.description_teaser'
        db.alter_column('o_t_itineraire', 'description_teaser', self.gf('django.db.models.fields.TextField')())

        # Renaming column for 'Trek.access' to match new field type.
        db.rename_column('o_t_itineraire', 'acces', 'access')
        # Changing field 'Trek.access'
        db.alter_column('o_t_itineraire', 'access', self.gf('django.db.models.fields.TextField')())

        # Renaming column for 'Trek.advice_it' to match new field type.
        db.rename_column('o_t_itineraire', 'recommandation_it', 'advice_it')
        # Changing field 'Trek.advice_it'
        db.alter_column('o_t_itineraire', 'advice_it', self.gf('django.db.models.fields.TextField')(null=True))

        # Renaming column for 'Trek.description_teaser_it' to match new field type.
        db.rename_column('o_t_itineraire', 'chapeau_it', 'description_teaser_it')
        # Changing field 'Trek.description_teaser_it'
        db.alter_column('o_t_itineraire', 'description_teaser_it', self.gf('django.db.models.fields.TextField')(null=True))

        # Renaming column for 'Trek.arrival' to match new field type.
        db.rename_column('o_t_itineraire', 'arrivee', 'arrival')
        # Changing field 'Trek.arrival'
        db.alter_column('o_t_itineraire', 'arrival', self.gf('django.db.models.fields.CharField')(max_length=128))

        # Renaming column for 'Trek.departure_fr' to match new field type.
        db.rename_column('o_t_itineraire', 'depart_fr', 'departure_fr')
        # Changing field 'Trek.departure_fr'
        db.alter_column('o_t_itineraire', 'departure_fr', self.gf('django.db.models.fields.CharField')(max_length=128, null=True))

        # Changing field 'Trek.description'
        db.alter_column('o_t_itineraire', 'description', self.gf('django.db.models.fields.TextField')())

        # Renaming column for 'Trek.access_fr' to match new field type.
        db.rename_column('o_t_itineraire', 'acces_fr', 'access_fr')
        # Changing field 'Trek.access_fr'
        db.alter_column('o_t_itineraire', 'access_fr', self.gf('django.db.models.fields.TextField')(null=True))

        # Renaming column for 'Trek.advice' to match new field type.
        db.rename_column('o_t_itineraire', 'recommandation', 'advice')
        # Changing field 'Trek.advice'
        db.alter_column('o_t_itineraire', 'advice', self.gf('django.db.models.fields.TextField')())

        # Renaming column for 'Trek.disabled_infrastructure' to match new field type.
        db.rename_column('o_t_itineraire', 'handicap', 'disabled_infrastructure')
        # Changing field 'Trek.disabled_infrastructure'
        db.alter_column('o_t_itineraire', 'disabled_infrastructure', self.gf('django.db.models.fields.TextField')())

        # Changing field 'Trek.description_en'
        db.alter_column('o_t_itineraire', 'description_en', self.gf('django.db.models.fields.TextField')(null=True))

        # Renaming column for 'Trek.description_teaser_en' to match new field type.
        db.rename_column('o_t_itineraire', 'chapeau_en', 'description_teaser_en')
        # Changing field 'Trek.description_teaser_en'
        db.alter_column('o_t_itineraire', 'description_teaser_en', self.gf('django.db.models.fields.TextField')(null=True))

        # Renaming column for 'Trek.difficulty' to match new field type.
        db.rename_column('o_t_itineraire', 'difficulte', 'difficulty_id')
        # Changing field 'Trek.difficulty'
        db.alter_column('o_t_itineraire', 'difficulty_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['trekking.DifficultyLevel']))

        # Renaming column for 'Trek.disabled_infrastructure_fr' to match new field type.
        db.rename_column('o_t_itineraire', 'handicap_fr', 'disabled_infrastructure_fr')
        # Changing field 'Trek.disabled_infrastructure_fr'
        db.alter_column('o_t_itineraire', 'disabled_infrastructure_fr', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Trek.description_it'
        db.alter_column('o_t_itineraire', 'description_it', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Trek.ambiance_fr'
        db.alter_column('o_t_itineraire', 'ambiance_fr', self.gf('django.db.models.fields.TextField')(null=True))

        # Renaming column for 'Trek.advised_parking' to match new field type.
        db.rename_column('o_t_itineraire', 'parking', 'advised_parking')
        # Changing field 'Trek.advised_parking'
        db.alter_column('o_t_itineraire', 'advised_parking', self.gf('django.db.models.fields.CharField')(max_length=128))

        # Renaming column for 'Trek.advice_en' to match new field type.
        db.rename_column('o_t_itineraire', 'recommandation_en', 'advice_en')
        # Changing field 'Trek.advice_en'
        db.alter_column('o_t_itineraire', 'advice_en', self.gf('django.db.models.fields.TextField')(null=True))

        # Renaming column for 'Trek.name' to match new field type.
        db.rename_column('o_t_itineraire', 'nom', 'name')
        # Changing field 'Trek.name'
        db.alter_column('o_t_itineraire', 'name', self.gf('django.db.models.fields.CharField')(max_length=128))

        # Renaming column for 'Trek.disabled_infrastructure_it' to match new field type.
        db.rename_column('o_t_itineraire', 'handicap_it', 'disabled_infrastructure_it')
        # Changing field 'Trek.disabled_infrastructure_it'
        db.alter_column('o_t_itineraire', 'disabled_infrastructure_it', self.gf('django.db.models.fields.TextField')(null=True))

        # Renaming column for 'Trek.arrival_fr' to match new field type.
        db.rename_column('o_t_itineraire', 'arrivee_fr', 'arrival_fr')
        # Changing field 'Trek.arrival_fr'
        db.alter_column('o_t_itineraire', 'arrival_fr', self.gf('django.db.models.fields.CharField')(max_length=128, null=True))

        # Renaming column for 'Trek.access_it' to match new field type.
        db.rename_column('o_t_itineraire', 'acces_it', 'access_it')
        # Changing field 'Trek.access_it'
        db.alter_column('o_t_itineraire', 'access_it', self.gf('django.db.models.fields.TextField')(null=True))

        # Renaming column for 'Trek.route' to match new field type.
        db.rename_column('o_t_itineraire', 'parcours', 'route_id')
        # Changing field 'Trek.route'
        db.alter_column('o_t_itineraire', 'route_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['trekking.Route']))

        # Renaming column for 'Trek.departure' to match new field type.
        db.rename_column('o_t_itineraire', 'depart', 'departure')
        # Changing field 'Trek.departure'
        db.alter_column('o_t_itineraire', 'departure', self.gf('django.db.models.fields.CharField')(max_length=128))

        # Changing field 'Trek.ambiance_en'
        db.alter_column('o_t_itineraire', 'ambiance_en', self.gf('django.db.models.fields.TextField')(null=True))

        # Renaming column for 'Trek.public_transport' to match new field type.
        db.rename_column('o_t_itineraire', 'transport', 'public_transport')
        # Changing field 'Trek.public_transport'
        db.alter_column('o_t_itineraire', 'public_transport', self.gf('django.db.models.fields.TextField')())

        # Renaming column for 'Trek.disabled_infrastructure_en' to match new field type.
        db.rename_column('o_t_itineraire', 'handicap_en', 'disabled_infrastructure_en')
        # Changing field 'Trek.disabled_infrastructure_en'
        db.alter_column('o_t_itineraire', 'disabled_infrastructure_en', self.gf('django.db.models.fields.TextField')(null=True))

        # Renaming column for 'Trek.published' to match new field type.
        db.rename_column('o_t_itineraire', 'public', 'published')
        # Changing field 'Trek.published'
        db.alter_column('o_t_itineraire', 'published', self.gf('django.db.models.fields.BooleanField')())

        # Renaming column for 'Trek.advice_fr' to match new field type.
        db.rename_column('o_t_itineraire', 'recommandation_fr', 'advice_fr')
        # Changing field 'Trek.advice_fr'
        db.alter_column('o_t_itineraire', 'advice_fr', self.gf('django.db.models.fields.TextField')(null=True))

        # Renaming column for 'TrekNetwork.network_it' to match new field type.
        db.rename_column('o_b_reseau', 'reseau_it', 'network_it')
        # Changing field 'TrekNetwork.network_it'
        db.alter_column('o_b_reseau', 'network_it', self.gf('django.db.models.fields.CharField')(max_length=128, null=True))

        # Renaming column for 'TrekNetwork.network' to match new field type.
        db.rename_column('o_b_reseau', 'reseau', 'network')
        # Changing field 'TrekNetwork.network'
        db.alter_column('o_b_reseau', 'network', self.gf('django.db.models.fields.CharField')(max_length=128))

        # Renaming column for 'TrekNetwork.network_en' to match new field type.
        db.rename_column('o_b_reseau', 'reseau_en', 'network_en')
        # Changing field 'TrekNetwork.network_en'
        db.alter_column('o_b_reseau', 'network_en', self.gf('django.db.models.fields.CharField')(max_length=128, null=True))

        # Renaming column for 'TrekNetwork.network_fr' to match new field type.
        db.rename_column('o_b_reseau', 'reseau_fr', 'network_fr')
        # Changing field 'TrekNetwork.network_fr'
        db.alter_column('o_b_reseau', 'network_fr', self.gf('django.db.models.fields.CharField')(max_length=128, null=True))

        # Changing field 'Usage.usage_fr'
        db.alter_column('o_b_usage', 'usage_fr', self.gf('django.db.models.fields.CharField')(max_length=128, null=True))

        # Renaming column for 'Usage.pictogram' to match new field type.
        db.rename_column('o_b_usage', 'picto', 'pictogram')
        # Changing field 'Usage.pictogram'
        db.alter_column('o_b_usage', 'pictogram', self.gf('django.db.models.fields.files.FileField')(max_length=100))

        # Changing field 'Usage.usage_it'
        db.alter_column('o_b_usage', 'usage_it', self.gf('django.db.models.fields.CharField')(max_length=128, null=True))

        # Changing field 'Usage.usage_en'
        db.alter_column('o_b_usage', 'usage_en', self.gf('django.db.models.fields.CharField')(max_length=128, null=True))

        # Changing field 'Usage.usage'
        db.alter_column('o_b_usage', 'usage', self.gf('django.db.models.fields.CharField')(max_length=128))

        # Renaming column for 'WebLink.category' to match new field type.
        db.rename_column('o_t_web', 'categorie', 'category_id')
        # Changing field 'WebLink.category'
        db.alter_column('o_t_web', 'category_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['trekking.WebLinkCategory']))

        # Renaming column for 'WebLink.name_fr' to match new field type.
        db.rename_column('o_t_web', 'nom_fr', 'name_fr')
        # Changing field 'WebLink.name_fr'
        db.alter_column('o_t_web', 'name_fr', self.gf('django.db.models.fields.CharField')(max_length=128, null=True))

        # Renaming column for 'WebLink.name_it' to match new field type.
        db.rename_column('o_t_web', 'nom_it', 'name_it')
        # Changing field 'WebLink.name_it'
        db.alter_column('o_t_web', 'name_it', self.gf('django.db.models.fields.CharField')(max_length=128, null=True))

        # Renaming column for 'WebLink.name' to match new field type.
        db.rename_column('o_t_web', 'nom', 'name')
        # Changing field 'WebLink.name'
        db.alter_column('o_t_web', 'name', self.gf('django.db.models.fields.CharField')(max_length=128))

        # Changing field 'WebLink.url'
        db.alter_column('o_t_web', 'url', self.gf('django.db.models.fields.URLField')(max_length=128))

        # Renaming column for 'WebLink.name_en' to match new field type.
        db.rename_column('o_t_web', 'nom_en', 'name_en')
        # Changing field 'WebLink.name_en'
        db.alter_column('o_t_web', 'name_en', self.gf('django.db.models.fields.CharField')(max_length=128, null=True))

        # Renaming column for 'TrekRelationship.trek_a' to match new field type.
        db.rename_column('o_r_itineraire_itineraire', 'itineraire_a', 'trek_a_id')
        # Changing field 'TrekRelationship.trek_a'
        db.alter_column('o_r_itineraire_itineraire', 'trek_a_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['trekking.Trek']))

        # Renaming column for 'TrekRelationship.trek_b' to match new field type.
        db.rename_column('o_r_itineraire_itineraire', 'itineraire_b', 'trek_b_id')
        # Changing field 'TrekRelationship.trek_b'
        db.alter_column('o_r_itineraire_itineraire', 'trek_b_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['trekking.Trek']))

        # Renaming column for 'TrekRelationship.has_common_departure' to match new field type.
        db.rename_column('o_r_itineraire_itineraire', 'depart_commun', 'has_common_departure')
        # Changing field 'TrekRelationship.has_common_departure'
        db.alter_column('o_r_itineraire_itineraire', 'has_common_departure', self.gf('django.db.models.fields.BooleanField')())

        # Renaming column for 'TrekRelationship.is_circuit_step' to match new field type.
        db.rename_column('o_r_itineraire_itineraire', 'etape_circuit', 'is_circuit_step')
        # Changing field 'TrekRelationship.is_circuit_step'
        db.alter_column('o_r_itineraire_itineraire', 'is_circuit_step', self.gf('django.db.models.fields.BooleanField')())

        # Renaming column for 'TrekRelationship.has_common_edge' to match new field type.
        db.rename_column('o_r_itineraire_itineraire', 'troncons_communs', 'has_common_edge')
        # Changing field 'TrekRelationship.has_common_edge'
        db.alter_column('o_r_itineraire_itineraire', 'has_common_edge', self.gf('django.db.models.fields.BooleanField')())

        # Renaming column for 'Route.route_it' to match new field type.
        db.rename_column('o_b_parcours', 'parcours_it', 'route_it')
        # Changing field 'Route.route_it'
        db.alter_column('o_b_parcours', 'route_it', self.gf('django.db.models.fields.CharField')(max_length=128, null=True))

        # Renaming column for 'Route.route_fr' to match new field type.
        db.rename_column('o_b_parcours', 'parcours_fr', 'route_fr')
        # Changing field 'Route.route_fr'
        db.alter_column('o_b_parcours', 'route_fr', self.gf('django.db.models.fields.CharField')(max_length=128, null=True))

        # Renaming column for 'Route.route_en' to match new field type.
        db.rename_column('o_b_parcours', 'parcours_en', 'route_en')
        # Changing field 'Route.route_en'
        db.alter_column('o_b_parcours', 'route_en', self.gf('django.db.models.fields.CharField')(max_length=128, null=True))

        # Renaming column for 'Route.route' to match new field type.
        db.rename_column('o_b_parcours', 'parcours', 'route')
        # Changing field 'Route.route'
        db.alter_column('o_b_parcours', 'route', self.gf('django.db.models.fields.CharField')(max_length=128))

        # Renaming column for 'Theme.label_it' to match new field type.
        db.rename_column('o_b_theme', 'theme_it', 'label_it')
        # Changing field 'Theme.label_it'
        db.alter_column('o_b_theme', 'label_it', self.gf('django.db.models.fields.CharField')(max_length=128, null=True))

        # Renaming column for 'Theme.pictogram' to match new field type.
        db.rename_column('o_b_theme', 'picto', 'pictogram')
        # Changing field 'Theme.pictogram'
        db.alter_column('o_b_theme', 'pictogram', self.gf('django.db.models.fields.files.FileField')(max_length=100))

        # Renaming column for 'Theme.label' to match new field type.
        db.rename_column('o_b_theme', 'theme', 'label')
        # Changing field 'Theme.label'
        db.alter_column('o_b_theme', 'label', self.gf('django.db.models.fields.CharField')(max_length=128))

        # Renaming column for 'Theme.label_en' to match new field type.
        db.rename_column('o_b_theme', 'theme_en', 'label_en')
        # Changing field 'Theme.label_en'
        db.alter_column('o_b_theme', 'label_en', self.gf('django.db.models.fields.CharField')(max_length=128, null=True))

        # Renaming column for 'Theme.label_fr' to match new field type.
        db.rename_column('o_b_theme', 'theme_fr', 'label_fr')
        # Changing field 'Theme.label_fr'
        db.alter_column('o_b_theme', 'label_fr', self.gf('django.db.models.fields.CharField')(max_length=128, null=True))

        # Renaming column for 'DifficultyLevel.difficulty_it' to match new field type.
        db.rename_column('o_b_difficulte', 'difficulte_it', 'difficulty_it')
        # Changing field 'DifficultyLevel.difficulty_it'
        db.alter_column('o_b_difficulte', 'difficulty_it', self.gf('django.db.models.fields.CharField')(max_length=128, null=True))

        # Renaming column for 'DifficultyLevel.difficulty' to match new field type.
        db.rename_column('o_b_difficulte', 'difficulte', 'difficulty')
        # Changing field 'DifficultyLevel.difficulty'
        db.alter_column('o_b_difficulte', 'difficulty', self.gf('django.db.models.fields.CharField')(max_length=128))

        # Renaming column for 'DifficultyLevel.difficulty_fr' to match new field type.
        db.rename_column('o_b_difficulte', 'difficulte_fr', 'difficulty_fr')
        # Changing field 'DifficultyLevel.difficulty_fr'
        db.alter_column('o_b_difficulte', 'difficulty_fr', self.gf('django.db.models.fields.CharField')(max_length=128, null=True))

        # Renaming column for 'DifficultyLevel.difficulty_en' to match new field type.
        db.rename_column('o_b_difficulte', 'difficulte_en', 'difficulty_en')
        # Changing field 'DifficultyLevel.difficulty_en'
        db.alter_column('o_b_difficulte', 'difficulty_en', self.gf('django.db.models.fields.CharField')(max_length=128, null=True))

        # Renaming column for 'WebLinkCategory.label_it' to match new field type.
        db.rename_column('o_b_web_category', 'nom_it', 'label_it')
        # Changing field 'WebLinkCategory.label_it'
        db.alter_column('o_b_web_category', 'label_it', self.gf('django.db.models.fields.CharField')(max_length=128, null=True))

        # Renaming column for 'WebLinkCategory.pictogram' to match new field type.
        db.rename_column('o_b_web_category', 'picto', 'pictogram')
        # Changing field 'WebLinkCategory.pictogram'
        db.alter_column('o_b_web_category', 'pictogram', self.gf('django.db.models.fields.files.FileField')(max_length=100))

        # Renaming column for 'WebLinkCategory.label' to match new field type.
        db.rename_column('o_b_web_category', 'nom', 'label')
        # Changing field 'WebLinkCategory.label'
        db.alter_column('o_b_web_category', 'label', self.gf('django.db.models.fields.CharField')(max_length=128))

        # Renaming column for 'WebLinkCategory.label_en' to match new field type.
        db.rename_column('o_b_web_category', 'nom_en', 'label_en')
        # Changing field 'WebLinkCategory.label_en'
        db.alter_column('o_b_web_category', 'label_en', self.gf('django.db.models.fields.CharField')(max_length=128, null=True))

        # Renaming column for 'WebLinkCategory.label_fr' to match new field type.
        db.rename_column('o_b_web_category', 'nom_fr', 'label_fr')
        # Changing field 'WebLinkCategory.label_fr'
        db.alter_column('o_b_web_category', 'label_fr', self.gf('django.db.models.fields.CharField')(max_length=128, null=True))

        # Renaming column for 'POI.name_fr' to match new field type.
        db.rename_column('o_t_poi', 'nom_fr', 'name_fr')
        # Changing field 'POI.name_fr'
        db.alter_column('o_t_poi', 'name_fr', self.gf('django.db.models.fields.CharField')(max_length=128, null=True))

        # Renaming column for 'POI.name_it' to match new field type.
        db.rename_column('o_t_poi', 'nom_it', 'name_it')
        # Changing field 'POI.name_it'
        db.alter_column('o_t_poi', 'name_it', self.gf('django.db.models.fields.CharField')(max_length=128, null=True))

        # Renaming column for 'POI.name' to match new field type.
        db.rename_column('o_t_poi', 'nom', 'name')
        # Changing field 'POI.name'
        db.alter_column('o_t_poi', 'name', self.gf('django.db.models.fields.CharField')(max_length=128))

        # Changing field 'POI.description_en'
        db.alter_column('o_t_poi', 'description_en', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'POI.description_fr'
        db.alter_column('o_t_poi', 'description_fr', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'POI.description_it'
        db.alter_column('o_t_poi', 'description_it', self.gf('django.db.models.fields.TextField')(null=True))

        # Renaming column for 'POI.name_en' to match new field type.
        db.rename_column('o_t_poi', 'nom_en', 'name_en')
        # Changing field 'POI.name_en'
        db.alter_column('o_t_poi', 'name_en', self.gf('django.db.models.fields.CharField')(max_length=128, null=True))

        # Renaming column for 'POI.type' to match new field type.
        db.rename_column('o_t_poi', 'type', 'type_id')
        # Changing field 'POI.type'
        db.alter_column('o_t_poi', 'type_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['trekking.POIType']))

        # Changing field 'POI.description'
        db.alter_column('o_t_poi', 'description', self.gf('django.db.models.fields.TextField')())

        # Renaming column for 'POIType.label_it' to match new field type.
        db.rename_column('o_b_poi', 'nom_it', 'label_it')
        # Changing field 'POIType.label_it'
        db.alter_column('o_b_poi', 'label_it', self.gf('django.db.models.fields.CharField')(max_length=128, null=True))

        # Renaming column for 'POIType.pictogram' to match new field type.
        db.rename_column('o_b_poi', 'picto', 'pictogram')
        # Changing field 'POIType.pictogram'
        db.alter_column('o_b_poi', 'pictogram', self.gf('django.db.models.fields.files.FileField')(max_length=100))

        # Renaming column for 'POIType.label' to match new field type.
        db.rename_column('o_b_poi', 'nom', 'label')
        # Changing field 'POIType.label'
        db.alter_column('o_b_poi', 'label', self.gf('django.db.models.fields.CharField')(max_length=128))

        # Renaming column for 'POIType.label_en' to match new field type.
        db.rename_column('o_b_poi', 'nom_en', 'label_en')
        # Changing field 'POIType.label_en'
        db.alter_column('o_b_poi', 'label_en', self.gf('django.db.models.fields.CharField')(max_length=128, null=True))

        # Renaming column for 'POIType.label_fr' to match new field type.
        db.rename_column('o_b_poi', 'nom_fr', 'label_fr')
        # Changing field 'POIType.label_fr'
        db.alter_column('o_b_poi', 'label_fr', self.gf('django.db.models.fields.CharField')(max_length=128, null=True))

    models = {
        'authent.structure': {
            'Meta': {'object_name': 'Structure'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'core.comfort': {
            'Meta': {'object_name': 'Comfort', 'db_table': "'l_b_confort'"},
            'comfort': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']"})
        },
        'core.datasource': {
            'Meta': {'object_name': 'Datasource', 'db_table': "'l_b_source'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']"})
        },
        'core.network': {
            'Meta': {'object_name': 'Network', 'db_table': "'l_b_reseau'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'network': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']"})
        },
        'core.path': {
            'Meta': {'object_name': 'Path', 'db_table': "'l_t_troncon'"},
            'arrival': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'db_column': "'arrivee'", 'blank': 'True'}),
            'ascent': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'denivelee_positive'"}),
            'comfort': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'paths'", 'null': 'True', 'to': "orm['core.Comfort']"}),
            'comments': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'remarques'", 'blank': 'True'}),
            'datasource': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'paths'", 'null': 'True', 'to': "orm['core.Datasource']"}),
            'date_insert': ('django.db.models.fields.DateTimeField', [], {}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {}),
            'departure': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'db_column': "'depart'", 'blank': 'True'}),
            'descent': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'denivelee_negative'"}),
            'geom': ('django.contrib.gis.db.models.fields.LineStringField', [], {'srid': '%s' % settings.SRID, 'dim': '3', 'spatial_index': 'False'}),
            'geom_cadastre': ('django.contrib.gis.db.models.fields.LineStringField', [], {'srid': '%s' % settings.SRID, 'dim': '3', 'null': 'True', 'spatial_index': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.FloatField', [], {'default': '0', 'db_column': "'longueur'"}),
            'max_elevation': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'altitude_maximum'"}),
            'min_elevation': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'altitude_minimum'"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'db_column': "'nom_troncon'", 'blank': 'True'}),
            'networks': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'paths'", 'to': "orm['core.Network']", 'db_table': "'l_r_troncon_reseau'", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'stake': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'paths'", 'null': 'True', 'to': "orm['core.Stake']"}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']"}),
            'trail': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'paths'", 'null': 'True', 'to': "orm['core.Trail']"}),
            'usages': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'paths'", 'to': "orm['core.Usage']", 'db_table': "'l_r_troncon_usage'", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'valid': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_column': "'troncon_valide'"})
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
            'stake': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']"})
        },
        'core.topology': {
            'Meta': {'object_name': 'Topology', 'db_table': "'e_t_evenement'"},
            'date_insert': ('django.db.models.fields.DateTimeField', [], {}),
            'date_update': ('django.db.models.fields.DateTimeField', [], {}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'supprime'"}),
            'geom': ('django.contrib.gis.db.models.fields.GeometryField', [], {'srid': '%s' % settings.SRID, 'dim': '3', 'null': 'True', 'spatial_index': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'length': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'db_column': "'longueur'"}),
            'offset': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'db_column': "'decallage'"}),
            'paths': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['core.Path']", 'through': "orm['core.PathAggregation']", 'db_column': "'troncons'", 'symmetrical': 'False'})
        },
        'core.trail': {
            'Meta': {'object_name': 'Trail', 'db_table': "'l_t_sentier'"},
            'arrival': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'comments': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'departure': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']"})
        },
        'core.usage': {
            'Meta': {'object_name': 'Usage', 'db_table': "'l_b_usage'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'structure': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['authent.Structure']"}),
            'usage': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'trekking.difficultylevel': {
            'Meta': {'object_name': 'DifficultyLevel', 'db_table': "'o_b_difficulte'"},
            'difficulty': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'difficulte'"}),
            'difficulty_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'difficulte'", 'blank': 'True'}),
            'difficulty_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'difficulte'", 'blank': 'True'}),
            'difficulty_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'difficulte'", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'trekking.poi': {
            'Meta': {'object_name': 'POI', 'db_table': "'o_t_poi'", '_ormbases': ['core.Topology']},
            'description': ('django.db.models.fields.TextField', [], {'db_column': "'description'"}),
            'description_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'description'", 'blank': 'True'}),
            'description_fr': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'description'", 'blank': 'True'}),
            'description_it': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'description'", 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'nom'"}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'name_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'name_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'topo_object': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Topology']", 'unique': 'True', 'primary_key': 'True', 'db_column': "'evenement'"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pois'", 'db_column': "'type'", 'to': "orm['trekking.POIType']"})
        },
        'trekking.poitype': {
            'Meta': {'object_name': 'POIType', 'db_table': "'o_b_poi'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'nom'"}),
            'label_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'label_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'label_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'pictogram': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'db_column': "'picto'"})
        },
        'trekking.route': {
            'Meta': {'object_name': 'Route', 'db_table': "'o_b_parcours'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'route': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'parcours'"}),
            'route_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'parcours'", 'blank': 'True'}),
            'route_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'parcours'", 'blank': 'True'}),
            'route_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'parcours'", 'blank': 'True'})
        },
        'trekking.theme': {
            'Meta': {'object_name': 'Theme', 'db_table': "'o_b_theme'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'theme'"}),
            'label_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'theme'", 'blank': 'True'}),
            'label_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'theme'", 'blank': 'True'}),
            'label_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'theme'", 'blank': 'True'}),
            'pictogram': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'db_column': "'picto'"})
        },
        'trekking.trek': {
            'Meta': {'object_name': 'Trek', 'db_table': "'o_t_itineraire'", '_ormbases': ['core.Topology']},
            'access': ('django.db.models.fields.TextField', [], {'db_column': "'acces'", 'blank': 'True'}),
            'access_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'acces'", 'blank': 'True'}),
            'access_fr': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'acces'", 'blank': 'True'}),
            'access_it': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'acces'", 'blank': 'True'}),
            'advice': ('django.db.models.fields.TextField', [], {'db_column': "'recommandation'", 'blank': 'True'}),
            'advice_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'recommandation'", 'blank': 'True'}),
            'advice_fr': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'recommandation'", 'blank': 'True'}),
            'advice_it': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'recommandation'", 'blank': 'True'}),
            'advised_parking': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'parking'", 'blank': 'True'}),
            'ambiance': ('django.db.models.fields.TextField', [], {'db_column': "'ambiance'", 'blank': 'True'}),
            'ambiance_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'ambiance'", 'blank': 'True'}),
            'ambiance_fr': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'ambiance'", 'blank': 'True'}),
            'ambiance_it': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'ambiance'", 'blank': 'True'}),
            'arrival': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'arrivee'", 'blank': 'True'}),
            'arrival_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'arrivee'", 'blank': 'True'}),
            'arrival_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'arrivee'", 'blank': 'True'}),
            'arrival_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'arrivee'", 'blank': 'True'}),
            'ascent': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'denivelee_positive'"}),
            'departure': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'depart'", 'blank': 'True'}),
            'departure_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'depart'", 'blank': 'True'}),
            'departure_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'depart'", 'blank': 'True'}),
            'departure_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'depart'", 'blank': 'True'}),
            'descent': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'denivelee_negative'"}),
            'description': ('django.db.models.fields.TextField', [], {'db_column': "'description'", 'blank': 'True'}),
            'description_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'description'", 'blank': 'True'}),
            'description_fr': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'description'", 'blank': 'True'}),
            'description_it': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'description'", 'blank': 'True'}),
            'description_teaser': ('django.db.models.fields.TextField', [], {'db_column': "'chapeau'", 'blank': 'True'}),
            'description_teaser_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'chapeau'", 'blank': 'True'}),
            'description_teaser_fr': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'chapeau'", 'blank': 'True'}),
            'description_teaser_it': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'chapeau'", 'blank': 'True'}),
            'difficulty': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'treks'", 'null': 'True', 'db_column': "'difficulte'", 'to': "orm['trekking.DifficultyLevel']"}),
            'disabled_infrastructure': ('django.db.models.fields.TextField', [], {'db_column': "'handicap'"}),
            'disabled_infrastructure_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'handicap'", 'blank': 'True'}),
            'disabled_infrastructure_fr': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'handicap'", 'blank': 'True'}),
            'disabled_infrastructure_it': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_column': "'handicap'", 'blank': 'True'}),
            'duration': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'duree'", 'blank': 'True'}),
            'is_park_centered': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'coeur'"}),
            'max_elevation': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'altitude_maximum'"}),
            'min_elevation': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_column': "'altitude_minimum'"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'nom'"}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'name_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'name_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'networks': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'treks'", 'to': "orm['trekking.TrekNetwork']", 'db_table': "'o_r_itineraire_reseau'", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'parking_location': ('django.contrib.gis.db.models.fields.PointField', [], {'srid': '%s' % settings.SRID, 'null': 'True', 'spatial_index': 'False', 'db_column': "'geom_parking'", 'blank': 'True'}),
            'public_transport': ('django.db.models.fields.TextField', [], {'db_column': "'transport'", 'blank': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'public'"}),
            'route': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'treks'", 'null': 'True', 'db_column': "'parcours'", 'to': "orm['trekking.Route']"}),
            'themes': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'treks'", 'to': "orm['trekking.Theme']", 'db_table': "'o_r_itineraire_theme'", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'topology_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Topology']", 'unique': 'True', 'primary_key': 'True'}),
            'usages': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'treks'", 'to': "orm['trekking.Usage']", 'db_table': "'o_r_itineraire_usage'", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'web_links': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'treks'", 'to': "orm['trekking.WebLink']", 'db_table': "'o_r_itineraire_web'", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'})
        },
        'trekking.treknetwork': {
            'Meta': {'object_name': 'TrekNetwork', 'db_table': "'o_b_reseau'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'network': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'reseau'"}),
            'network_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'reseau'", 'blank': 'True'}),
            'network_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'reseau'", 'blank': 'True'}),
            'network_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'reseau'", 'blank': 'True'})
        },
        'trekking.trekrelationship': {
            'Meta': {'unique_together': "(('trek_a', 'trek_b'),)", 'object_name': 'TrekRelationship', 'db_table': "'o_r_itineraire_itineraire'"},
            'has_common_departure': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'depart_commun'"}),
            'has_common_edge': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'troncons_communs'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_circuit_step': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_column': "'etape_circuit'"}),
            'trek_a': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'trek_relationship_a'", 'db_column': "'itineraire_a'", 'to': "orm['trekking.Trek']"}),
            'trek_b': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'trek_relationship_b'", 'db_column': "'itineraire_b'", 'to': "orm['trekking.Trek']"})
        },
        'trekking.usage': {
            'Meta': {'object_name': 'Usage', 'db_table': "'o_b_usage'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pictogram': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'db_column': "'picto'"}),
            'usage': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'usage'"}),
            'usage_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'usage'", 'blank': 'True'}),
            'usage_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'usage'", 'blank': 'True'}),
            'usage_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'usage'", 'blank': 'True'})
        },
        'trekking.weblink': {
            'Meta': {'object_name': 'WebLink', 'db_table': "'o_t_web'"},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'links'", 'null': 'True', 'db_column': "'categorie'", 'to': "orm['trekking.WebLinkCategory']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'nom'"}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'name_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'name_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '128', 'db_column': "'url'"})
        },
        'trekking.weblinkcategory': {
            'Meta': {'object_name': 'WebLinkCategory', 'db_table': "'o_b_web_category'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_column': "'nom'"}),
            'label_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'label_fr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'label_it': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'db_column': "'nom'", 'blank': 'True'}),
            'pictogram': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'db_column': "'picto'"})
        }
    }

    complete_apps = ['trekking']