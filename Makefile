SHELL = /bin/bash

port=8000
host=0.0.0.0
listen=$(host):$(port)
baseurl=http://$(listen)
user=$(shell whoami)
version=$(shell git describe --tags --abbrev=0)

ROOT_DIR=$(shell pwd)
BUILDOUT_CFG = $(ROOT_DIR)/conf/buildout.cfg
BUILDOUT_VERSION = 1.7.1
BUILDOUT_BOOTSTRAP_URL = http://downloads.buildout.org/2/bootstrap.py
BUILDOUT_BOOTSTRAP = bootstrap.py
BUILDOUT_BOOTSTRAP_ARGS = -c $(BUILDOUT_CFG) --buildout-version=$(BUILDOUT_VERSION) buildout:directory=$(ROOT_DIR)
BUILDOUT = bin/buildout
BUILDOUT_ARGS = -N buildout:directory=$(ROOT_DIR) buildout:user=$(user)


.PHONY: all_makemessages all_compilemessages install clean_harmless clean env_dev env_test env_prod env_standalone tests test test_nav test_js serve deploy load_data load_demo


etc/settings.ini:
	mkdir -p etc/
	cp conf/settings.ini.sample etc/settings.ini
	chmod -f 600 etc/settings.ini

bin/python:
	virtualenv -p /usr/bin/python2 .
	bin/pip install -U setuptools
	mkdir -p lib/src
	mkdir -p lib/eggs
	wget --quiet -O $(BUILDOUT_BOOTSTRAP) $(BUILDOUT_BOOTSTRAP_URL)
	bin/python $(BUILDOUT_BOOTSTRAP) $(BUILDOUT_BOOTSTRAP_ARGS)
	rm $(BUILDOUT_BOOTSTRAP)

install: etc/settings.ini bin/python

clean_harmless:
	find . -name "*.orig" -exec rm -f {} \;
	find geotrek/ -name "*.pyc" -exec rm -f {} \;
	-find lib/src/ -name "*.pyc" -exec rm -f {} \;
	rm -f install
	rm -f .coverage

clean: clean_harmless
	rm -rf bin/ lib/ local/ include/ *.egg-info/
	rm -rf var/cache
	rm -rf var/log
	rm -rf var/run
	rm -rf var/static
	rm -rf var/tmp
	rm -rf etc/init/
	rm -rf etc/*.cfg
	rm -rf etc/*.conf
	rm -f .installed.cfg



env_test: install clean_harmless
	$(BUILDOUT) -c conf/buildout-tests.cfg $(BUILDOUT_ARGS)

env_dev: install clean_harmless
	$(BUILDOUT) -c conf/buildout-dev.cfg $(BUILDOUT_ARGS)

env_prod: install clean_harmless
	$(BUILDOUT) -c conf/buildout-prod.cfg $(BUILDOUT_ARGS)

env_standalone: install clean_harmless
	$(BUILDOUT) -c conf/buildout-prod-standalone.cfg $(BUILDOUT_ARGS)



test:
	bin/django test --noinput geotrek

test_nav:
	casperjs test --baseurl=$(baseurl) geotrek/jstests/nav-*.js

test_export:
	casperjs test --baseurl=$(baseurl) geotrek/jstests/nav-auth.js geotrek/jstests/export-*.js


node_modules:
	npm install geotrek/jstests

test_js: node_modules
	./node_modules/geotrek-tests/node_modules/mocha-phantomjs/bin/mocha-phantomjs geotrek/jstests/index.html

tests: test test_js test_nav

serve:
	bin/django runserver_plus --threaded $(listen)

services:
	@echo "Stop convertit"
	kill `netstat -tlp 2>/dev/null | grep ':6543' | sed 's;.*LISTEN      \([0-9]*\)/python;\1;'`; true
	@echo "Stop screamshotter"
	kill `netstat -tlp 2>/dev/null | grep ':8001' | sed 's;.*LISTEN      \([0-9]*\)/python;\1;'`; true
	@echo "Start convertit"
	bin/convertit lib/src/convertit/development.ini &
	@echo "Start screamshotter"
	bin/django runserver --settings=screamshotter.settings 8001 &

update:
	bin/develop update -f
	bin/django collectstatic --clear --noinput --verbosity=0
	bin/django syncdb --noinput --migrate
	bin/django sync_translation_fields --noinput
	bin/django update_translation_fields
	bin/django update_permissions
	make all_compilemessages

deploy: update
	sudo service supervisor restart

all_makemessages:
	for dir in `find geotrek/ -type d -name locale`; do pushd `dirname $$dir` > /dev/null; $(ROOT_DIR)/bin/django-admin makemessages --no-location --all; popd > /dev/null; done

all_compilemessages:
	for dir in `find geotrek/ -type d -name locale`; do pushd `dirname $$dir` > /dev/null; $(ROOT_DIR)/bin/django-admin compilemessages; popd > /dev/null; done
	for dir in `find lib/src/ -type d -name locale`; do pushd `dirname $$dir` > /dev/null; $(ROOT_DIR)/bin/django-admin compilemessages; popd > /dev/null; done



load_data:
	# /!\ will delete existing data
	bin/django loaddata minimal
	bin/django loaddata cirkwi
	bin/django loaddata basic
	for dir in `find geotrek/ -type d -name upload`; do pushd `dirname $$dir` > /dev/null; cp -R upload/* $(ROOT_DIR)/var/media/upload/ ; popd > /dev/null; done

load_demo: load_data
	bin/django loaddata development-pne

css:
	for f in `find geotrek/ -name '*.scss'`; do node-sass --output-style=expanded $$f -o `dirname $$f`; done