#!/usr/bin/python3
import os
import distutils.command.build
from pathlib import Path
from setuptools import setup, find_packages
from shutil import copy

here = os.path.abspath(os.path.dirname(__file__))


class BuildCommand(distutils.command.build.build):
    def run(self):
        distutils.command.build.build.run(self)
        from django.core.management import call_command
        curdir = os.getcwd()
        for subdir in ('geotrek', 'mapentity'):
            os.chdir(subdir)
            call_command('compilemessages')
            for path in Path('.').rglob('*.mo'):
                copy(path, os.path.join(curdir, self.build_lib, subdir, path))
            os.chdir(curdir)

setup(
    name='geotrek',
    version=open(os.path.join(here, 'VERSION')).read().strip(),
    author='Makina Corpus',
    author_email='geobi@makina-corpus.com',
    url='http://makina-corpus.com',
    description="Geotrek",
    long_description=(open(os.path.join(here, 'README.rst')).read() + '\n\n'
                      + open(os.path.join(here, 'docs', 'changelog.rst')).read()),
    scripts=['manage.py'],
    install_requires=[
        # pinned by requirements.txt
        'psycopg2',
        'docutils',
        'Pillow',
        'easy-thumbnails',
        'simplekml',
        'pygal',
        'django-extended-choices',
        'django-mptt',
        'django-multiselectfield',
        'geojson',
        'tif2geojson',
        'pytz',
        'djangorestframework-gis',
        'drf-dynamic-fields',
        'drf-yasg',
        'django-embed-video',
        'xlrd',
        'landez',
        'redis',
        'celery',
        'django-celery-results',
        'requests[security]',
        'drf-extensions',
        'django-colorfield',
        'factory_boy',
        'Fiona'
    ],
    cmdclass={"build": BuildCommand},
    include_package_data=True,
    license='BSD, see LICENSE file.',
    packages=find_packages(),
    classifiers=['Natural Language :: English',
                 'Environment :: Web Environment',
                 'Framework :: Django',
                 'Development Status :: 5 - Production/Stable',
                 'Programming Language :: Python :: 2.7'],
)
