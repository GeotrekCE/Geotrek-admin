#### /!\ Only for fresh installations, for others please upgrade to geotrek 2.18.6 /!\

## USE a script

```bash
wget --no-check-certificate --content-disposition https://raw.githubusercontent.com/LePetitTim/Geotrek-admin/docker-install/install/install.sh
```
## ----------------------------------------------------------
## INSTALL Docker and Docker-Compose
Check your Linux distribution :
```bash
sudo cat /etc/issue
```
Find the most adequate docker install in :
https://docs.docker.com/install/linux/docker-ce/ubuntu/

And Docker-Compose :
https://docs.docker.com/compose/install/#install-compose

## CREATE a dedicated user
Do the following 3 commands :

```bash
useradd geotrek
adduser geotrek sudo
adduser geotrek docker
```

## MOVE your folder

Move and rename this folder according to your instance name

ex : 

```bash
cd .. # If you are inside the folder install
mv install /path/of/your/instance/geotrek
```
*Later in this install /path/of/your/instance/geotrek is /srv/geotrek*

## FIX rights and LOGIN with your user for all operations
```bash
chown -R geotrek:geotrek /srv/geotrek
su - geotrek
```

# COPY environment of install

Copy .env.dist to .env

```bash
cd /srv/geotrek
cp ./install/.env.dist .env

```

## SET environment variables

Open .env and complete it
```dotenv
POSTGRES_USER=<your_personnal_database_user>
POSTGRES_DB=<your_personnal_database_user>
POSTGRES_PASSWORD=<your_personnal_database_password>
DOMAIN_NAME=<your.geotrek.com>
SECRET_KEY=<your_personnal_secret_key>
```
**If you use external database, make sure postgresql > 9.3
and postgis > 2.1, add these environment variables**
```dotenv
POSTGRES_HOST=<your_host_or_ip>
POSTGRES_PORT=<your_port>
```
**and comment postgresql section in docker-compose.yml**
```python

```
## CREATE the var folder
```bash
mkdir -p var
docker-compose run web /bin/sh -c exit
```

## EDIT your custom.py file
Set at least MODELTRANSLATION_LANGUAGES / SRID / SPATIAL_EXTENT / DEFAULT_STRUCTURE_NAME:

*You need to use sudo*

ex:

```bash
cd ./var/conf
sudo vi custom.py
sudo nano custom.py
# ...
```

```python

MODELTRANSLATION_LANGUAGES = ('en', 'fr', 'it', 'es')

SRID = 2154

SPATIAL_EXTENT = (105000, 6150000, 1100000, 7150000)

DEFAULT_STRUCTURE_NAME = 'GEOTEAM'
```


## INITIATE database

```bash
docker-compose run postgres -d
```

## INITIATE required data

```bash
docker-compose run web initial.sh
```

## CREATE your first superuser

```bash
docker-compose run web ./manage.py createsuperuser
```

## I you want to use SSL
Put your certificate and key in this folder
Uncomment and edit docker-compose.yml nginx section
Edit custom.py and fix ssl section
Edit your geotrek_nginx.conf with mounted path of your files

## INSTALL geotrek as service
Edit *geotrek.service* file to fix 
WorkingDirectory with your absolute geotrek folder path
and enable it
```bash
sudo cp geotrek.service /etc/systemd/system/geotrek.service
sudo systemctl enable geotrek
```

## RUN, STOP, UPDATE geotrek
For run and stop your geotrek instance do this command :
```bash
sudo systemctl start geotrek
sudo systemctl stop geotrek
```

**Check the other commands in the doc**

## BACKUP

You can use *backup.sh* to make a tar with your database dump + customization (this folder)
don't forget to save it on another place