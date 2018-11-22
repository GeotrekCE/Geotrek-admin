LOCAL_USER_ID=$(shell id -u)

var:
	mkdir var

build:
	LOCAL_USER_ID=$(LOCAL_USER_ID) docker-compose build

build-no-cache:
	LOCAL_USER_ID=$(LOCAL_USER_ID) docker-compose build --no-cache

serve:
	docker-compose up

test:
	docker-compose run web test --settings=geotrek.settings.test

test_nav:
	casperjs test --baseurl=$(baseurl) geotrek/jstests/nav-*.js

test_export:
	casperjs test --baseurl=$(baseurl) geotrek/jstests/nav-auth.js geotrek/jstests/export-*.js

node_modules:
	npm install geotrek/jstests

test_js: node_modules
	./node_modules/.bin/mocha-phantomjs geotrek/jstests/index.html

tests: test test_js test_nav

update:
	docker-compose run web update.sh

load_data:
	docker-compose run web initial.sh

load_demo: load_data
	docker-compose run web ./manage.py loaddata development-pne

css:
	for f in `find geotrek/ -name '*.scss'`; do node-sass --output-style=expanded $$f -o `dirname $$f`; done

