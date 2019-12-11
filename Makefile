build:
	docker build -t geotrek .

build-no-cache:
	docker build -t geotrek --no-cache .

serve:
	docker-compose up

test:
	docker-compose -e ENV=tests run web ./manage.py test

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
	docker-compose run web load_data.sh

load_demo:
	docker-compose run web ./manage.py loaddata development-pne

css:
	for f in `find geotrek/ -name '*.scss'`; do node-sass --output-style=expanded $$f -o `dirname $$f`; done
