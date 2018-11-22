PWD=$(shell pwd)
pwdesc=$(shell echo $(PWD) | sed 's_/_\\/_g')

init:
	mkdir -p var

install: init
	sudo systemctl daemon-reload
	#sed -i "s/^\(WorkingDirectory=\).*/\1$(pwdesc)/" geotrek.service;
	sudo cp geotrek.service /etc/systemd/system/geotrek.service
	docker-compose up -d postgres
	@docker-compose run web /bin/sh -c exit
	sudo systemctl enable geotrek
	@echo "Please custom your conf/custom.py with your SRID at least, then run make initial"

initial:
	docker-compose run web initial.sh
	docker-compose run web ./manage.py createsuperuser

update:
	sudo systemctl stop geotrek
	docker pull nginx:1.15
	docker pull makinacorpus/screamshotter
	docker pull makinacorpus/convertit
	docker pull makinacorpus/postgis:11-2.5
	docker pull redis:5.0-alpine
	docker pull memcached:1.5-alpine
	docker-compose run web update.sh
	sudo systemctl start geotrek

upgrade:
	docker pull geotrekce/admin:latest
	update