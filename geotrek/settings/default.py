
# import os
#
# from django.conf.global_settings import LANGUAGES as LANGUAGES_LIST
# from django.contrib.gis.geos import fromstr


# FORCE_SCRIPT_NAME = ROOT_URL if ROOT_URL != '' else None
# SYNC_RANDO_ROOT = envini.get('syncrandoroot', section="django", default=os.path.join(DEPLOY_ROOT, 'data'))
#
# MAILALERTSUBJECT = envini.get('mailalertsubject', section="settings", default="")
# MAILALERTMESSAGE = envini.get('mailalertmessage', section="settings", default="")

#
# EMAIL_SUBJECT_PREFIX = '[%s] ' % TITLE
#
# #
# # Deployment settings
# # ..........................
# TEMPLATES[1]['DIRS'] = (os.path.join(DEPLOY_ROOT, 'geotrek', 'templates'),
#                         os.path.join(DEPLOY_ROOT, 'lib', 'parts', 'omelette',
#                                      'mapentity', 'templates'),
#                         os.path.join(MEDIA_ROOT, 'templates')) + TEMPLATES[1]['DIRS']
#

#
# SRID = int(envini.get('srid', SRID))
# SPATIAL_EXTENT = tuple(envini.getfloats('spatial_extent'))
#
# LEAFLET_CONFIG['TILES_EXTENT'] = SPATIAL_EXTENT
# LEAFLET_CONFIG['SPATIAL_EXTENT'] = api_bbox(SPATIAL_EXTENT, VIEWPORT_MARGIN)
#
# MAP_STYLES['path']['color'] = envini.get('layercolor_paths', MAP_STYLES['path']['color'])
# MAP_STYLES['city']['color'] = envini.get('layercolor_land', MAP_STYLES['city']['color'])
# MAP_STYLES['district']['color'] = envini.get('layercolor_land', MAP_STYLES['district']['color'])
#
# _others_color = envini.get('layercolor_others', None)
# if _others_color:
#     MAP_STYLES.setdefault('detail', {})['color'] = _others_color
#     MAP_STYLES.setdefault('others', {})['color'] = _others_color
