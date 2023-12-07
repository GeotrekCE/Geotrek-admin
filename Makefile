ifeq (, $(shell which docker-compose))
  docker_compose=docker compose
else
  docker_compose=docker-compose
endif

###########################
#          colors         #
###########################
PRINT_COLOR = printf
COLOR_SUCCESS = \033[1;32m
COLOR_DEBUG = \033[36m
COLOR_RESET = \033[0m

build:
	docker build -t geotrek . --build-arg BASE_IMAGE_TAG=$(BASE_IMAGE_TAG)

build-no-cache:
	docker build -t geotrek --no-cache .

build_deb:
	docker pull $(DISTRO)
	docker build -t geotrek_deb -f ./docker/Dockerfile.debian.builder --build-arg DISTRO=$(DISTRO) .
	docker run --name geotrek_deb_run -t geotrek_deb bash -c "exit"
	docker cp geotrek_deb_run:/dpkg ./
	docker stop geotrek_deb_run
	docker rm geotrek_deb_run

serve:
	$(docker_compose) up

deps:
	$(docker_compose) run --rm web bash -c "pip-compile -q && pip-compile -q dev-requirements.in"

flake8:
	$(docker_compose) run --rm web flake8 geotrek

messages:
	$(docker_compose) run --rm web ./manage.py makemessages -a --no-location

###########################
#        coverage         #
###########################
verbose_level ?= 1
.PHONY: coverage
coverage:
	@$(PRINT_COLOR) "$(COLOR_SUCCESS) ### Start coverage ### $(COLOR_RESET)\n"
	$(docker_compose) run -e ENV=tests web coverage run ./manage.py test $(test_name) -v $(verbose_level)
	$(docker_compose) run -e ENV=tests_nds web coverage run -a ./manage.py test $(test_name) -v $(verbose_level)
	$(docker_compose) run -e ENV=tests web coverage lcov

test:
	$(docker_compose) run -e ENV=tests --rm web ./manage.py test

test_nds:
	$(docker_compose) run -e ENV=tests_nds --rm web ./manage.py test

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
	$(docker_compose) run web update.sh

load_data:
	$(docker_compose) run web load_data.sh

load_demo:
	$(docker_compose) run web ./manage.py loaddata development-pne

load_test_integration:
	$(docker_compose) run web ./manage.py loaddata test-integration

css:
	for f in `find geotrek/ -name '*.scss'`; do node-sass --output-style=expanded $$f -o `dirname $$f`; done

%.pdf:
	mkdir -p docs/data-model
	postgresql_autodoc -h localhost -u geotrek -d geotrekdb -t dot -m "$*_.*" --password=geotrek -s "public"
	dot geotrekdb.dot -T pdf -o docs/data-model/$@
	rm geotrekdb.dot

authent.pdf:
	mkdir -p docs/data-model
	postgresql_autodoc -h localhost -u geotrek -d geotrekdb -t dot -m "auth(ent)?_.*" --password=geotrek -s "public"
	dot geotrekdb.dot -T pdf -o docs/data-model/authent.pdf
	rm geotrekdb.dot

global.pdf:
	postgresql_autodoc -h localhost -u geotrek -d geotrekdb -t dot --password=geotrek -s "public"
	dot geotrekdb.dot -T pdf -o docs/data-model/global.pdf
	rm geotrekdb.dot

uml: authent.pdf cirkwi.pdf core.pdf diving.pdf feedback.pdf flatpages.pdf infrastructure.pdf land.pdf maintenance.pdf outdoor.pdf sensitivity.pdf signage.pdf tourism.pdf trekking.pdf zoning.pdf global.pdf
