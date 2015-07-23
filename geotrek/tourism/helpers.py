import logging
import json

import geojson
from tif2geojson import tif2geojson

from geotrek.tourism.models import DATA_SOURCE_TYPES


logger = logging.getLogger(__name__)


def post_process(source, language, content):

    if source.type == DATA_SOURCE_TYPES.GEOJSON:
        try:
            result = json.loads(content)
            assert result.get('type') == 'FeatureCollection'
            assert result.get('features') is not None
            return result
        except (ValueError, AssertionError) as e:
            logger.error(u"Source '%s' returns invalid GeoJSON" % source.url)
            logger.exception(e)
            raise

    elif source.type == DATA_SOURCE_TYPES.TOURINFRANCE:
        return tif2geojson(content, lang=language)

    elif source.type == DATA_SOURCE_TYPES.SITRA:
        try:
            result = json.loads(content)
            objects = result.get('objetsTouristiques')
            assert objects is not None
            return sitra_to_geojson(objects, language)
        except (ValueError, AssertionError) as e:
            logger.error(u"Source '%s' returns invalid SITA json" % source.url)
            logger.exception(e)
            raise

    else:
        raise NotImplementedError


def sitra_to_geojson(objects, language):

    def key_lang(d, key, lang):
        lang_key = '%s%s' % (key, language.title())
        default_key = '%s%s' % (key, 'Fr')
        return d.get(lang_key, d.get(default_key))

    def find_by_type(values, typeid):
        for value in values:
            if value.get('type', {}).get('id') == typeid:
                return value
        return {}

    features = []

    for objdict in objects:

        name = key_lang(objdict['nom'], 'libelle', language)
        description = key_lang(objdict.get('presentation', {}).get('descriptifCourt', {}), 'libelle', language)
        website = find_by_type(objdict.get('informations', {}).get('moyensCommunication', {}), 205).get('coordonnees')
        if website:
            website = website.get('fr')
        phone = find_by_type(objdict.get('informations', {}).get('moyensCommunication', {}), 201).get('coordonnees')
        if phone:
            phone = phone.get('fr')
        geometry = objdict.get('localisation', {}).get('geolocalisation', {}).get('geoJson')

        pictures = []
        illustrations = objdict.get('illustrations', [])
        for illustration in illustrations:
            picture = {}
            picture['url'] = illustration.get('traductionFichiers', [{}])[0].get('url')
            picture['legend'] = key_lang(illustration.get('nom', {}), 'libelle', language)
            picture['copyright'] = key_lang(illustration.get('copyright', {}), 'libelle', language)
            pictures.append(picture)

        id_ = objdict['id']
        properties = {}
        properties['title'] = name
        properties['category'] = objdict['type']
        properties['description'] = description
        properties['website'] = website
        properties['phone'] = phone
        properties['pictures'] = pictures

        feature = geojson.Feature(id=id_,
                                  geometry=geometry,
                                  properties=properties)
        features.append(feature)

    result = geojson.FeatureCollection(features)
    return result
