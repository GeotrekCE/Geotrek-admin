ifeq (, $(shell which docker-compose))
  docker_compose=docker compose
else
  docker_compose=docker-compose
endif

-include Makefile.perso.mk

###########################
#          colors         #
###########################
PRINT_COLOR = printf
COLOR_SUCCESS = \033[1;32m
COLOR_DEBUG = \033[36m
COLOR_RESET = \033[0m

build:
	docker build -t geotrek -f docker/Dockerfile . --build-arg BASE_IMAGE_TAG=$(BASE_IMAGE_TAG)

build_no_cache:
	docker build -t geotrek -f docker/Dockerfile --no-cache .

build_deb:
	docker pull $(DISTRO)
	docker build -t geotrek_deb -f ./docker/Dockerfile.debian.builder --build-arg DISTRO=$(DISTRO) .
	docker run --name geotrek_deb_run -t geotrek_deb bash -c "exit"
	docker cp geotrek_deb_run:/dpkg ./
	docker stop geotrek_deb_run
	docker rm geotrek_deb_run

release:
	docker build -t geotrek_release -f ./docker/Dockerfile.debian.builder --target base .
	docker run --name geotrek_release -v ./debian:/dpkg-build/debian -it geotrek_release  bash -c "dch -r -D RELEASED"
	docker stop geotrek_release
	docker rm geotrek_release


serve:
	$(docker_compose) up

deps:
	$(docker_compose) run --rm web bash -c "pip-compile -q --strip-extras && pip-compile -q --strip-extras dev-requirements.in && pip-compile -q --strip-extras docs/requirements.in"

flake8:
	$(docker_compose) run --rm web flake8 geotrek

messages:
	$(docker_compose) run --rm web ./manage.py makemessages -a --no-location --no-obsolete

compilemessages:
	$(docker_compose) run --rm web ./manage.py compilemessages

###########################
#        coverage         #
###########################
verbose_level ?= 1
report ?= report -m
.PHONY: coverage
coverage:
	rm ./var/.coverage* || true
	@$(PRINT_COLOR) "$(COLOR_SUCCESS) ### Start coverage ### $(COLOR_RESET)\n"
	$(docker_compose) run -e ENV=tests web coverage run --parallel-mode --concurrency=multiprocessing ./manage.py test $(test_name) --noinput --parallel -v $(verbose_level)
	$(docker_compose) run -e ENV=tests_nds web coverage run --parallel-mode --concurrency=multiprocessing ./manage.py test $(test_name) --noinput --parallel -v $(verbose_level)
	$(docker_compose) run -e ENV=tests web bash -c "coverage combine && coverage $(report)"
	rm ./var/.coverage*

test:
	$(docker_compose) run -e ENV=tests --rm web ./manage.py test --shuffle --noinput --parallel

test_nds:
	$(docker_compose) run -e ENV=tests_nds --rm web ./manage.py test --shuffle --noinput --parallel

tests: test test_nds

update:
	$(docker_compose) run web update.sh

load_data:
	$(docker_compose) run web load_data.sh

load_demo:
	$(docker_compose) run web ./manage.py loaddata development-pne

load_test_integration:
	$(docker_compose) run web ./manage.py loaddata test-integration

clean_data:
	$(docker_compose) down -v --remove-orphans
	rm -rf var/cache/*
	rm -rf var/tiles/*
	rm -rf var/media/*
	rm -rf var/static/*
	rm -rf var/tmp/*
	rm -rf var/log/*
	rm -rf var/mobile/*


flush: clean_data update load_data

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
