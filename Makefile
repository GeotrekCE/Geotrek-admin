SHELL = /bin/bash

listen=localhost:8000
baseurl=http://$(listen)
root=$(shell pwd)
version=$(shell git describe --tags --abbrev=0)

bin/ lib/:
	virtualenv .
	wget http://python-distribute.org/bootstrap.py
	bin/python bootstrap.py
	rm bootstrap.py

install: bin/

clean_harmless:
	find caminae/ -name "*.pyc" -exec rm {} \;

clean: clean_harmless
	rm -rf bin/ lib/ local/ include/ *.egg-info/ develop-eggs/ parts/
	rm -rf reports/ var/
	rm -f .installed.cfg

.PHONY: all_makemessages all_compilemessages

all_makemessages: bin/
	for dir in `find caminae/ -type d -name locale`; do pushd `dirname $$dir` > /dev/null; $(root)/bin/django-admin makemessages -a; popd > /dev/null; done

all_compilemessages: bin/
	for dir in `find caminae/ -type d -name locale`; do pushd `dirname $$dir` > /dev/null; $(root)/bin/django-admin compilemessages; popd > /dev/null; done

release:
	git archive --format=zip --prefix="caminae-$(version)/" $(version) > ../caminae-src-$(version).zip

unit_tests: bin/ clean_harmless
	bin/buildout -Nvc buildout-tests.cfg
	bin/develop update -f
	bin/django jenkins --coverage-rcfile=.coveragerc authent core land maintenance trekking common infrastructure mapentity

functional_tests:
	casperjs --baseurl=$(baseurl) --save=reports/FUNC-auth.xml caminae/tests/auth.js
	casperjs --baseurl=$(baseurl) --save=reports/FUNC-88.xml caminae/tests/story_88_user_creation.js

tests: unit_tests functional_tests

serve: bin/ clean_harmless all_compilemessages
	bin/buildout -Nvc buildout-dev.cfg
	bin/django syncdb --noinput --migrate
	bin/django runserver $(listen)

load_data:
	# /!\ will delete existing data
	bin/django loaddata development-pne

deploy: bin/ clean_harmless all_compilemessages
	bin/buildout -Nvc buildout-prod.cfg
	bin/django syncdb --noinput --migrate
	bin/django collectstatic --noinput
	bin/supervisorctl restart all

deploy_demo: deploy load_data
