SHELL = /bin/bash

listen=localhost:8000
baseurl=http://$(listen)
user=$(shell whoami)
version=$(shell git describe --tags --abbrev=0)

ROOT_DIR=$(shell pwd)
BUILDOUT_CFG = $(ROOT_DIR)/conf/buildout.cfg
BUILDOUT_VERSION = 1.7.1
BUILDOUT_BOOTSTRAP_URL = http://downloads.buildout.org/2/bootstrap.py
BUILDOUT_BOOTSTRAP = bootstrap.py
BUILDOUT_BOOTSTRAP_ARGS = -c $(BUILDOUT_CFG) --version=$(BUILDOUT_VERSION) buildout:directory=$(ROOT_DIR)
BUILDOUT = bin/buildout
BUILDOUT_ARGS = -N buildout:directory=$(ROOT_DIR) buildout:user=$(user)


.PHONY: all_makemessages all_compilemessages install clean_harmless clean env_dev env_test env_prod env_standalone tests test test_nav test_js serve deploy load_data deploy_demo


etc/settings.ini:
	mkdir -p etc/
	cp conf/settings.ini.sample etc/settings.ini
	chmod -f 600 etc/settings.ini

bin/python:
	virtualenv .
	mkdir -p lib/eggs
	wget --quiet -O $(BUILDOUT_BOOTSTRAP) $(BUILDOUT_BOOTSTRAP_URL)
	bin/python $(BUILDOUT_BOOTSTRAP) $(BUILDOUT_BOOTSTRAP_ARGS)
	rm $(BUILDOUT_BOOTSTRAP)

install: etc/settings.ini bin/python

clean_harmless:
	find geotrek/ -name "*.pyc" -exec rm -f {} \;
	-find lib/src/ -name "*.pyc" -exec rm -f {} \;
	rm -f install

clean: clean_harmless
	rm -rf bin/ lib/ local/ include/ *.egg-info/
	rm -rf var/
	rm -rf etc/init/
	rm -f .installed.cfg
	rm -f install.log



all_makemessages: install
	for dir in `find geotrek/ -type d -name locale`; do pushd `dirname $$dir` > /dev/null; $(ROOT_DIR)/bin/django-admin makemessages --no-location --all; popd > /dev/null; done

all_compilemessages: install
	for dir in `find geotrek/ -type d -name locale`; do pushd `dirname $$dir` > /dev/null; $(ROOT_DIR)/bin/django-admin compilemessages; popd > /dev/null; done

env_test: install clean_harmless
	$(BUILDOUT) -c conf/buildout-tests.cfg $(BUILDOUT_ARGS)

env_dev: install clean_harmless all_compilemessages
	$(BUILDOUT) -c conf/buildout-dev.cfg $(BUILDOUT_ARGS)
	bin/django syncdb --noinput --migrate

env_prod: install clean_harmless
	$(BUILDOUT) -c conf/buildout-prod.cfg $(BUILDOUT_ARGS)

env_standalone: install clean_harmless
	$(BUILDOUT) -c conf/buildout-prod-standalone.cfg $(BUILDOUT_ARGS)



test:
	bin/django test --noinput geotrek

test_nav:
	for navtest in `ls geotrek/jstests/nav-*.js`; do casperjs --baseurl=$(baseurl) --save=var/reports/nav-`basename $$navtest`.xml $$navtest; done

node_modules:
	npm install geotrek/jstests

test_js: node_modules
	./node_modules/geotrek-tests/node_modules/mocha-phantomjs/bin/mocha-phantomjs geotrek/jstests/index.html

tests: test test_js test_nav

serve:
	bin/django runserver_plus $(listen)

deploy:
	make all_compilemessages
	bin/develop update -f
	bin/django syncdb --noinput --migrate
	bin/django collectstatic --clear --noinput --verbosity=0
	bin/django update_translation_fields
	bin/supervisorctl restart all



load_data:
	# /!\ will delete existing data
	bin/django loaddata minimal
	bin/django loaddata basic
	for dir in `find geotrek/ -type d -name upload`; do pushd `dirname $$dir` > /dev/null; cp -R upload/* $(ROOT_DIR)/var/media/upload/ ; popd > /dev/null; done

deploy_demo: deploy load_data
	bin/django loaddata development-pne
