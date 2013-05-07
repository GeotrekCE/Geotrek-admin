#!/usr/bin/python
# -*- coding: utf8 -*-
import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

test_requirements = [
    'factory_boy == 1.1.5',
]


setup(
    name='geotrek',
    version=open(os.path.join(here, 'VERSION')).read().strip(),
    author='Makina Corpus',
    author_email='geobi@makina-corpus.com',
    url='http://makina-corpus.com',
    description="Geotrek",
    long_description=open(os.path.join(here, 'README.rst')).read(),
    install_requires=[
        'South == 0.7.6',
        'psycopg2 == 2.4.1',
        'GDAL == 1.9.1',  # installed by buildout, see include-dirs
        'Pillow == 1.7.8',
        'easy-thumbnails == 1.1',
        'simplekml == 1.2.1',
        'django-extended-choices',  # pinned by buildout
        'mapentity',  # pinned by buildout
    ] + test_requirements,
    tests_requires=test_requirements,
    packages=find_packages(),
    classifiers=['Natural Language :: English',
                 'Environment :: Web Environment',
                 'Framework :: Django',
                 'Development Status :: 5 - Production/Stable',
                 'Programming Language :: Python :: 2.5'],
)
