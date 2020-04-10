#!/usr/bin/python3
import os
import distutils.command.build
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))


class BuildCommand(distutils.command.build.build):
    def run(self):
        print("before")
        distutils.command.build.build.run(self)
        print("after")
        from django.core.management import call_command
        curdir = os.getcwd()
        os.chdir(os.path.join(curdir, 'geotrek'))
        call_command('compilemessages')
        os.chdir(os.path.join(curdir, 'mapentity'))
        call_command('compilemessages')
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
        'GDAL',
        'Pillow',
        'easy-thumbnails',
        'simplekml',
        'pygal',
        'django-extended-choices',
        'django-multiselectfield',
        'geojson',
        'tif2geojson',
        'pytz',
        'djangorestframework-gis',
        'drf-dynamic-fields',
        'django-rest-swagger',
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
