# ONLY FOR FRESH INSTALL AT NOW FOR OTHERS -> upgrade to geotrek 2.18.6

# INSTALL DOCKER
https://docs.docker.com/install/linux/docker-ce/ubuntu/

# INSTALL DOCKER COMPOSE
https://docs.docker.com/compose/install/#install-compose

# CREATE a dedicated user
useradd geotrek
adduser geotrek sudo
adduser geotrek docker


# move and rename this folder according your instance name

ex : 

```bash
cd ..
mv install /srv/geotrek

```

# Fix rights and login with your user for all operations
chown -R geotrek:geotrek /srv/geotrek
su - geotrek

# COPY .env.dist TO .env

```bash
cd /srv/geotrek
cp .env.dist .env

```

# SET environment variables in it

```dotenv
POSTGRES_USER=<your_personnal_database_user>
POSTGRES_DB=<your_personnal_database_user>
POSTGRES_PASSWORD=<your_personnal_database_password>
DOMAIN_NAME=<your_personnal_database_user>
#DOMAIN_NAME=your.geotrek.com
SECRET_KEY=<your_personnal_secret_key>
```

# Using external database (make sure postgresql > 9.3 and postgis > 2.1)

add these environment variables

```dotenv
POSTGRES_HOST=<your_host_or_ip>
POSTGRES_PORT=<your_port>
```

and comment postgresql section in docker-compose.yml

# Edit your custom.py file
# SET LANGUAGES / SRID / SPATIAL_EXTENT / DEFAULT_STRUCTURE_NAME at least

# INITIATE database

```bash
docker-compose run postgres -d
```

# INITIATE required data
```bash
docker-compose run web ./django/initial.sh
```

# Create your first superuser
```bash
docker-compose run web ./manage.py createsuperuser
```

# I you want to use SSL
put your certificate and key in this folder
uncomment and edit docker-compose.yml nginx section
edit custom.py and fix ssl section
edit your geotrek_nginx.conf with mounted path of your files

# Install geotrek as service
edit geotrek.service file to fix 
WorkingDirectory with your absolute geotrek folder path
and enable it
```bash
sudo cp geotrek.service /etc/systemd/system/geotrek.service
sudo systemctl enable geotrek
```

# Run and stop geotrek
```bash
sudo systemctl stop geotrek
sudo systemctl start geotrek
```

# backup

you can use backup.sh to make a tar with your database dump + customization (this folder)
don't forget to save it on another place