test_nav:
	casperjs test --baseurl=$(baseurl) geotrek/jstests/nav-*.js

test_export:
	casperjs test --baseurl=$(baseurl) geotrek/jstests/nav-auth.js geotrek/jstests/export-*.js


node_modules:
	npm install geotrek/jstests

test_js: node_modules
	./node_modules/.bin/mocha-phantomjs geotrek/jstests/index.html

tests: test test_js test_nav

serve:
	bin/django runserver_plus --threaded $(listen)

services:
	@echo "Stop convertit"
	kill $(shell netstat -tlp 2>/dev/null | grep ':6543' | sed 's;.*LISTEN      \([0-9]*\)/python.*;\1;'); true
	@echo "Stop screamshotter"
	kill $(shell netstat -tlp 2>/dev/null | grep ':8001' | sed 's;.*LISTEN      \([0-9]*\)/python.*;\1;'); true
	@echo "Start convertit"
	bin/convertit lib/src/convertit/development.ini &
	@echo "Start screamshotter"
	bin/django runserver --settings=screamshotter.settings 8001 &

update:
	bin/develop update -f
	bin/django collectstatic --clear --noinput --verbosity=0
	bin/django migrate --noinput
	bin/django sync_translation_fields --noinput
	bin/django update_translation_fields
	bin/django update_geotrek_permissions
	make all_compilemessages

load_demo: load_data
	bin/django loaddata development-pne

css:
	for f in `find geotrek/ -name '*.scss'`; do node-sass --output-style=expanded $$f -o `dirname $$f`; done

