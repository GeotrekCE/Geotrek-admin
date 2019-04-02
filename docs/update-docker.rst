#### _This file describe how to update geotrek instance on geotrek docker server_


### Save database

- Launch backup script

   ```bash
   $ ./backup.sh
   ```

## Update docker image

- Get future image version

   ```bash
   $ docker pull geotrekce/admin:<tag>
   ```

- Edit GEOTREK_VERSION for the new version in the file .env

   ```bash
   GEOTREK_VERSION=geotrek_version  <--
   POSTGRES_HOST=172.17.0.1
   POSTGRES_USER=your_database_user
   POSTGRES_DB=your_database
   POSTGRES_PASSWORD=your_user_password
   DOMAIN_NAME=your.final.geotrek.domain
   SECRET_KEY=secret-and-unique-secret-and-unique
   GUNICORN_CMD_ARGS=--bind=0.0.0.0:8000 --workers=5 --timeout=600
   # CONVERSION_HOST=convertit_web
   # CAPTURE_HOST=screamshotter_web
   ```
For the version of geotrek check : https://hub.docker.com/r/geotrekce/admin/tags/

- Restart the containers

    ```bash
    $ systemctl restart <instance_name>
    ```

- Run the update script
    ```bash
    $ docker-compose run --rm web update.sh
    ```
