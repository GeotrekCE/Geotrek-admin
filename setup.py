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
    url='http://geotrek.fr',
    description="Geotrek",
    long_description=(open(os.path.join(here, 'README.rst')).read() + '\n\n'
                      + open(os.path.join(here, 'docs', 'changelog.rst')).read()),
    install_requires=[
        'celery[redis]>=4.1.0',
        'django-celery-results>=1.0.1',
        'django-extended-choices>=1.3',
        'django-rest-swagger>=2.1.2',
        'drf-dynamic-fields>=0.2.0',
        'drf-extensions>=0.3.1',
        'geojson>=2.3.0',
        'gunicorn>=19.6.0',
        'landez>=2.4.0',
        'lxml>=3.4.4',
        'mapentity>=4.3.3',
        'psycopg2>=2.5.4',
        'pygal>=1.6.2',
        'python-memcached>=1.51',
        'simplekml>=1.3.0',
        'xlrd>=0.9.3',
    ],
    license='BSD, see LICENSE file.',
    packages=find_packages(),
    classifiers=['Natural Language :: English',
                 'Environment :: Web Environment',
                 'Framework :: Django',
                 'Development Status :: 5 - Production/Stable',
                 'Programming Language :: Python :: 3.5'],
)
