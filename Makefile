update:
	./docker/update.sh
	make restart

load_data:
	./docker/load_data.sh

restart:
	sudo supervisorctl restart all
