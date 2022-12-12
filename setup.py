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
        for subdir in ('geotrek', ):
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
    url='https://makina-corpus.com',
    description="Geotrek",
    long_description=(open(os.path.join(here, 'README.rst')).read() + '\n\n'
                      + open(os.path.join(here, 'docs', 'changelog.rst')).read()),
    scripts=['manage.py'],
    install_requires=[
        'Django==3.2.*',
        'mapentity==8.3.0',
        'cairosvg',
        'cairocffi==0.9.0',  # Latest version dh-virtualenv can handle to build the .deb package
        'env_file',
        # pinned by requirements.txt
        'pymemcache',
        'psycopg2',
        'pdfimpose',
        'docutils',
        'Pillow',
        'simplekml',
        'pygal',
        'paperclip',
        'django-extended-choices',
        'django-modelcluster',
        'django-mptt',
        'geojson',
        'tif2geojson',
        'drf-dynamic-fields',
        'drf-yasg',
        'xlrd',
        'landez',
        'celery[redis]',
        'django-celery-results==2.2.*',  # Latest version supporting python3.6
        'drf-extensions',
        'django-colorfield',
        'Fiona',
        'markdown',
        "weasyprint==52.5",  # newer version required libpango (not available in bionic)
        'django-weasyprint<2.0.0',  # 2.10 require weasyprint > 53
        "django-clearcache@git+https://github.com/timonweb/django-clearcache.git@6de7994#egg=django-clearcache",  # commit working with py 3.6 and django 3.2
        # prod,
        'gunicorn',
        'sentry-sdk',
        # tests
        'freezegun',
        'coverage',
        'factory_boy',
        # dev,
        'django-extensions',
        'django-debug-toolbar',
    ],
    cmdclass={"build": BuildCommand},
    include_package_data=True,
    license='BSD, see LICENSE file.',
    packages=find_packages(),
    classifiers=['Natural Language :: English',
                 'Environment :: Web Environment',
                 'Framework :: Django',
                 'Development Status :: 5 - Production/Stable',
                 'Programming Language :: Python :: 3'],
)
