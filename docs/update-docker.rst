============
UPDATE
============

These instructions will update *Geotrek* on a dedicated server for production.

Save database
------------

Launch backup script
::
   ./backup.sh

Update docker image
------------

Get future image version
::
   docker pull geotrekce/admin:<tag>

Edit GEOTREK_VERSION for the new version in the file .env
::
   GEOTREK_VERSION=geotrek_version  <--
   POSTGRES_HOST=172.17.0.1
   POSTGRES_USER=your_database_user
   POSTGRES_DB=your_database
   POSTGRES_PASSWORD=your_user_password
   DOMAIN_NAME=your.final.geotrek.domain
   SECRET_KEY=secret-and-unique-secret-and-unique
   GUNICORN_CMD_ARGS=--bind=0.0.0.0:8000 --workers=5 --timeout=600

For the version of geotrek check : https://hub.docker.com/r/geotrekce/admin/tags/

Restart the containers
::
    systemctl restart <instance_name>

Run the update script
::
    docker-compose run --rm web update.sh
