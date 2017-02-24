#!/usr/bin/python
# -*- coding: utf8 -*-
import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

setup(
    name='geotrek',
    version=open(os.path.join(here, 'VERSION')).read().strip(),
    author='Makina Corpus',
    author_email='geobi@makina-corpus.com',
    url='http://makina-corpus.com',
    description="Geotrek",
    long_description=(open(os.path.join(here, 'README.rst')).read() + '\n\n' +
                      open(os.path.join(here, 'docs', 'changelog.rst')).read()),
    install_requires=[
        # pinned by buildout
        'psycopg2',
        'docutils',
        'GDAL',
        'Pillow',
        'easy-thumbnails',
        'simplekml',
        'pygal',
        'django-extended-choices',
        'django-multiselectfield',
        'geojson',
        'tif2geojson',
        'mapentity',
        'pytz',
        'djangorestframework-gis',
        'django-embed-video',
        'xlrd',
        'landez',
        'django-celery',
        'redis',
    ],
    license='BSD, see LICENSE file.',
    packages=find_packages(),
    classifiers=['Natural Language :: English',
                 'Environment :: Web Environment',
                 'Framework :: Django',
                 'Development Status :: 5 - Production/Stable',
                 'Programming Language :: Python :: 2.5'],
)
