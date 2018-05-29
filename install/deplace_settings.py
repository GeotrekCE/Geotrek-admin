import argparse
import os
try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser  # ver. < 3.0

config = ConfigParser({'title': "Geotrek",
                       'root_url': "",
                       'deployroot': "",
                       'staticurl': "",
                       'mediaurl_secure': "/media_secure/",
                       'cachetimeout': "28800",
                       'authent_dbname': "authentdb",
                       'authent_tablename': "",
                       'authent_engine': "postgresql_psycopg2",
                       'authent_dbuser': "",
                       'mailfrom': "admin@yourdomain.tld",
                       'host': "*",
                       'dbname': "geotrek_name"})

parser = argparse.ArgumentParser()
parser.add_argument("path_old")
parser.add_argument("path_new")
args = parser.parse_args()
config.read(args.path_old + "/etc/settings.ini")

if not config.has_section('django'):
    config.add_section('django')

file_custom = open(os.path.join(args.path_new, "var", "conf", "custom.py"), 'w+')

default_structure = config.get('settings', 'defaultstructure')
root_url = config.get('settings', 'root_url')
language_code = config.get('settings', 'language')
title = config.get('settings', 'title')
cachetimeout = config.get('settings', 'cachetimeout')
deploy_root = config.get('django', 'deployroot')
media_url_secure = config.get('django', 'mediaurl_secure')
static_url = config.get('django', 'staticurl')
file_custom.write("from .prod import *"
                  ""
                  "#\n"
                  "# BASIC SETTINGS\n"
                  "# ..............\n"
                  "# Default structure for newly created users \n"
                  "TITLE = '%s'\n"
                  "DEFAULT_STRUCTURE_NAME = '%s'\n"
                  "ROOT_URL = '%s'\n" % (title, default_structure, root_url))
if deploy_root:
    file_custom.write("DEPLOY_ROOT = '%s'\n" % deploy_root)
if static_url:
    file_custom.write("STATIC_URL = '%s%s'\n" % (root_url, static_url))
file_custom.write("MEDIA_URL_SECURE = '%s'\n"
                  "CACHES['default']['TIMEOUT'] = %s\n"
                  "CACHES['fat']['TIMEOUT'] = %s\n"
                  "LANGUAGE_CODE = '%s'  # for web interface. default to fr (French) \n"
                  % (media_url_secure, cachetimeout, cachetimeout, language_code))

modeltranslation_languages = config.get('settings', 'languages')

modeltranslation_languages = modeltranslation_languages .split(",")

file_custom.write("MODELTRANSLATION_LANGUAGES = (")
for language in modeltranslation_languages:
    file_custom.write("'%s', " % language)
file_custom.write(")\n")

srid = config.get('settings', 'srid')
spatial_extent = config.get("settings", "spatial_extent")

file_custom.write("\n#\n"
                  "#  GIS settings\n"
                  "# ..........................\n"
                  "SRID = %s # LAMBERT EXTENDED FOR FRANCE, used for geometric columns.\n"
                  "# Must be a projection in meters Fixed at install, don't change it after\n"
                  "SPATIAL_EXTENT = (%s)\n"
                  "# spatial bbox in your own projection (example here with 2154)\n"
                  "# this spatial_extent will limit map exploration, and will cut your raster imports\n"
                  % (srid, spatial_extent))

secret_key = config.get('settings', 'secret_key')

file_custom.write("\n#\n"
                  "# API secret key\n"
                  "# ..........................\n"
                  "SECRET_KEY = '%s' # your secret key\n\n" % secret_key)

default_from_email = config.get("settings", "mailfrom")
email_host = config.get("settings", "mailhost")
email_host_user = config.get("settings", "mailuser")
email_host_password = config.get("settings", "mailpassword")
email_host_port = config.get("settings", "mailport")
email_use_tls = config.get("settings", "mailtls")
email_use_ssl = config.get("settings", "mailssl")
file_custom.write("#\n"
                  "#  Email settings\n"
                  "# ..........................\n"
                  "DEFAULT_FROM_EMAIL = '%s'\n"
                  "# address will be set for sended emails (ex: noreply@yourdomain.net)\n"
                  "SERVER_EMAIL = DEFAULT_FROM_EMAIL\n"
                  "EMAIL_HOST = '%s'\n"
                  "EMAIL_HOST_USER = '%s'\n"
                  "EMAIL_HOST_PASWWORD = '%s'\n"
                  "EMAIL_HOST_PORT = '%s'\n"
                  "EMAIL_USE_TLS = %s\n"
                  "EMAIL_USE_SSL = %s\n"
                  % (default_from_email, email_host, email_host_user, email_host_password, email_host_port,
                     email_use_tls, email_use_ssl))

authent_tablename = config.get("settings", "authent_tablename")
authent_database = config.get("settings", "authent_dbname")
authent_dbuser = config.get("settings", "authent_dbuser")
authent_engine = config.get("settings", "authent_engine")
file_custom.write("\n#\n"
                  "# External authent if required\n"
                  "# ..........................\n"
                  "AUTHENT_TABLENAME = '%s'\n"
                  "AUTHENT_DATABASE = '%s'\n" % (authent_tablename, authent_database))

if authent_tablename:
    file_custom.write("AUTHENTICATION_BACKENDS = ('geotrek.authent.backend.DatabaseBackend',)\n"
                      "DATABASES[AUTHENT_DATABASE] = {}\n"
                      "DATABASES[AUTHENT_DATABASE]['ENGINE'] = 'django.db.backends.%s'\n"
                      "DATABASES[AUTHENT_DATABASE]['NAME'] = '%s'\n"
                      "DATABASES[AUTHENT_DATABASE]['USER'] = '%s'\n"
                      % (authent_engine, authent_database, authent_dbuser))


admins = config.get("settings", "mailadmins")
admins = admins.split(",")
managers = config.get("settings", "mailmanagers")
managers = managers.split(",")

file_custom.write("\n#\n"
                  "#  Email settings\n"
                  "# ..........................\n"
                  "ADMINS = (")
for mail_admin in admins:
    file_custom.write("('Admin %s', '%s'), " % (title, mail_admin))

file_custom.write(")\n"
                  "MANAGERS = (")
for mail_manager in managers:
    file_custom.write("('Manager %s', '%s'), " % (title, mail_manager))
file_custom.write(")\n")

mailalertsubject = config.get("settings", "mailalertsubject")
mailalertmessage = config.get("settings", "mailalertmessage")

file_custom.write("MAILALERTSUBJECT = '%s'\n" % mailalertsubject)

file_custom.write('MAILALERTMESSAGE = """%s"""\n' % mailalertmessage)
try:
    file_custom.writelines([l for l in open(os.path.join(args.path_old, "geotrek", "settings", "custom.py")).readlines()])
except OSError as e:
    pass
file_custom.close()



file_env = open(args.path_new + ".env", 'w+')
db_name =  config.get("settings", "dbname")
db_user = config.get("settings", "dbuser")
db_password = config.get("settings", "dbpassword")
db_host = config.get("settings", "dbhost")
db_port = config.get("settings", "dbport")
host = config.get("settings", "host")
file_env.write("POSTGRES_DB = %s" % db_name)
file_env.write("POSTGRES_USER = %s" % db_user)
file_env.write("POSTGRES_PASSWORD = %s" % db_password)
file_env.write("POSTGRES_HOST = %s" % db_host)
file_env.write("POSTGRES_PORT = %s" % db_port)
file_env.write("DOMAIN_NAME = %s" % host)
file_env.write("SECRET_KEY= %s" % secret_key)
file_env.close()

