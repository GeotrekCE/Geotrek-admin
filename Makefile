build:
	docker build -t geotrek .

build-focal:
	docker build -t geotrek -f DockerfileFocal .

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

load_test_integration:
	docker-compose run web ./manage.py loaddata test-integration

css:
	for f in `find geotrek/ -name '*.scss'`; do node-sass --output-style=expanded $$f -o `dirname $$f`; done

%.pdf:
	mkdir -p docs/data-model
	postgresql_autodoc -h localhost -u geotrek -d geotrekdb -t dot -m "$*_.*"
	dot geotrekdb.dot -T pdf -o docs/data-model/$@
	rm geotrekdb.dot

authent.pdf:
	mkdir -p docs/data-model
	postgresql_autodoc -h localhost -u geotrek -d geotrekdb -t dot -m "auth(ent)?_.*"
	dot geotrekdb.dot -T pdf -o docs/data-model/authent.pdf
	rm geotrekdb.dot

global.pdf:
	postgresql_autodoc -h localhost -u geotrek -d geotrekdb -t dot
	dot geotrekdb.dot -T pdf -o docs/data-model/global.pdf
	rm geotrekdb.dot

uml: authent.pdf cirkwi.pdf core.pdf diving.pdf feedback.pdf flatpages.pdf infrastructure.pdf land.pdf maintenance.pdf sensitivity.pdf signage.pdf tourism.pdf trekking.pdf zoning.pdf global.pdf
