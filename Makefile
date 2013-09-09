SHELL = /bin/bash

listen=localhost:8000
baseurl=http://$(listen)
user=$(shell whoami)
version=$(shell git describe --tags --abbrev=0)
arch=$(shell uname -m)

ROOT_DIR=$(shell pwd)
BUILDOUT_CFG = $(ROOT_DIR)/conf/buildout.cfg
BUILDOUT_VERSION = 1.7.0
BUILDOUT_BOOTSTRAP_URL = https://raw.github.com/buildout/buildout/$(BUILDOUT_VERSION)/bootstrap/bootstrap.py
BUILDOUT_BOOTSTRAP = bootstrap.py
BUILDOUT_BOOTSTRAP_ARGS = -c $(BUILDOUT_CFG) --version=$(BUILDOUT_VERSION) --distribute buildout:directory=$(ROOT_DIR)
BUILDOUT = bin/buildout
BUILDOUT_ARGS = -N buildout:directory=$(ROOT_DIR) buildout:user=$(user)


etc/settings.ini:
	mkdir -p etc/
	cp conf/settings.ini.sample etc/settings.ini

bin/phantomjs:
	mkdir -p lib/
	wget http://phantomjs.googlecode.com/files/phantomjs-1.8.1-linux-$(arch).tar.bz2 -O phantomjs.tar.bz2
	rm -rf $(ROOT_DIR)/lib/*phantomjs*/
	tar -jxvf phantomjs.tar.bz2 -C $(ROOT_DIR)/lib/
	rm phantomjs.tar.bz2
	ln -sf $(ROOT_DIR)/lib/*phantomjs*/bin/phantomjs $(ROOT_DIR)/bin/

bin/casperjs: bin/phantomjs
	wget https://github.com/n1k0/casperjs/zipball/1.0.2 -O casperjs.zip
	rm -rf $(ROOT_DIR)/lib/*casperjs*/
	unzip -o casperjs.zip -d $(ROOT_DIR)/lib/ > /dev/null
	rm casperjs.zip
	ln -sf $(ROOT_DIR)/lib/*casperjs*/bin/casperjs $(ROOT_DIR)/bin/

bin/python:
	virtualenv .
	mkdir -p lib/eggs
	wget -O $(BUILDOUT_BOOTSTRAP) $(BUILDOUT_BOOTSTRAP_URL)
	bin/python $(BUILDOUT_BOOTSTRAP) $(BUILDOUT_BOOTSTRAP_ARGS)
	rm $(BUILDOUT_BOOTSTRAP)

install: etc/settings.ini bin/python bin/casperjs

clean_harmless:
	find geotrek/ -name "*.pyc" -exec rm -f {} \;
	rm -f install

clean: clean_harmless
	rm -rf bin/ lib/ local/ include/ *.egg-info/
	rm -rf var/
	rm -rf etc/init/
	rm -f .installed.cfg
	rm -f install.log

.PHONY: all_makemessages all_compilemessages

all_makemessages: install
	for dir in `find geotrek/ -type d -name locale`; do pushd `dirname $$dir` > /dev/null; $(ROOT_DIR)/bin/django-admin makemessages --no-location --all; popd > /dev/null; done

all_compilemessages: install
	for dir in `find geotrek/ -type d -name locale`; do pushd `dirname $$dir` > /dev/null; $(ROOT_DIR)/bin/django-admin compilemessages; popd > /dev/null; done
	for dir in `find lib/src/ -type d -name locale`; do pushd `dirname $$dir` > /dev/null; $(ROOT_DIR)/bin/django-admin compilemessages; popd > /dev/null; done

release:
	git archive --format=zip --prefix="geotrek-$(version)/" $(version) > ../geotrek-src-$(version).zip

test: install clean_harmless
	$(BUILDOUT) -c conf/buildout-tests.cfg $(BUILDOUT_ARGS)
	bin/develop update -f
	bin/django test --noinput authent core land maintenance trekking common infrastructure mapentity

test_nav:
	for navtest in `ls geotrek/jstests/nav-*.js`; do casperjs --baseurl=$(baseurl) --save=var/reports/nav-`basename $$navtest`.xml $$navtest; done

node_modules:
	npm install geotrek/jstests

test_js: node_modules
	./node_modules/geotrek-tests/node_modules/mocha-phantomjs/bin/mocha-phantomjs geotrek/jstests/index.html

tests: test test_js test_nav

serve: install clean_harmless all_compilemessages
	$(BUILDOUT) -c conf/buildout-dev.cfg $(BUILDOUT_ARGS)
	bin/django syncdb --noinput --migrate
	bin/django runserver_plus $(listen)

load_data:
	# /!\ will delete existing data
	bin/django loaddata minimal
	bin/django loaddata basic
	for dir in `find geotrek/ -type d -name upload`; do pushd `dirname $$dir` > /dev/null; cp -R upload/* $(ROOT_DIR)/var/media/upload/ ; popd > /dev/null; done

deploy: install clean_harmless
	$(BUILDOUT) -c conf/buildout-prod.cfg $(BUILDOUT_ARGS)
	make all_compilemessages
	bin/develop update -f
	bin/django syncdb --noinput --migrate
	bin/django collectstatic --clear --noinput --verbosity=0
	bin/django update_translation_fields
	bin/supervisorctl restart all

deploy_demo: deploy load_data
	bin/django loaddata development-pne
