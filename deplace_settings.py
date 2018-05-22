import argparse
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
                       'mailfrom': "admin@yourdomain.tld"})

parser = argparse.ArgumentParser()
parser.add_argument("path_ini")
args = parser.parse_args()
config.read(args.path_ini)

if not config.has_section('django'):
    config.add_section('django')

file_custom = open('geotrek/settings/custom.py', 'w')

default_structure = config.get('settings', 'defaultstructure')
root_url = config.get('settings', 'root_url')
language_code = config.get('settings', 'language')
title = config.get('settings', 'title')
cachetimeout = config.get('settings', 'cachetimeout')
deploy_root = config.get('django', 'deployroot')
media_url_secure = config.get('django', 'mediaurl_secure')
static_url = config.get('django', 'staticurl')
file_custom.write("#\n"
                  "# BASIC SETTINGS\n"
                  "# ..............\n"
                  "# Default structure for newly created users \n"
                  "TITLE = '" + title + "'\n"
                  "DEFAULT_STRUCTURE_NAME = '" + default_structure + "'\n"
                  "ROOT_URL = '" + root_url + "'\n")
if deploy_root:
    file_custom.write("DEPLOY_ROOT = '" + deploy_root + "'")
if static_url:
    file_custom.write("STATIC_URL = '" + root_url + static_url + "'")
file_custom.write("MEDIA_URL_SECURE = '" + media_url_secure + "'\n"
                  "CACHES['default']['TIMEOUT'] = " + cachetimeout + "\n"
                  "CACHES['fat']['TIMEOUT'] = " + cachetimeout + "\n"
                  "LANGUAGE_CODE = '" + language_code + "'  # for web interface. default to fr (French) \n")

modeltranslation_languages = config.get('settings', 'languages')

modeltranslation_languages = modeltranslation_languages .split(",")

file_custom.write("MODELTRANSLATION_LANGUAGES = (")
for language in modeltranslation_languages:
    file_custom.write("'" + language + "', ")
file_custom.write(")\n")

srid = config.get('settings', 'srid')
spatial_extent = config.get("settings", "spatial_extent")

file_custom.write("\n#\n"
                  "#  GIS settings\n"
                  "# ..........................\n"
                  "SRID = " + srid + " # LAMBERT EXTENDED FOR FRANCE, used for geometric columns.\n"
                  "# Must be a projection in meters Fixed at install, don't change it after\n"
                  "SPATIAL_EXTENT = (" + spatial_extent + ")\n"
                  "# spatial bbox in your own projection (example here with 2154)\n"
                  "# this spatial_extent will limit map exploration, and will cut your raster imports\n")

secret_key = config.get('settings', 'secret_key')

file_custom.write("\n#\n"
                  "# API secret key\n"
                  "# ..........................\n"
                  "SECRET_KEY = '" + secret_key + "' # your secret key\n\n")

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
                  "DEFAULT_FROM_EMAIL = '" + default_from_email + "'\n"
                  "# address will be set for sended emails (ex: noreply@yourdomain.net)\n"
                  "SERVER_EMAIL = DEFAULT_FROM_EMAIL\n"
                  "EMAIL_HOST = '" + email_host + "'\n"
                  "EMAIL_HOST_USER = '" + email_host_user + "'\n"
                  "EMAIL_HOST_PASWWORD = '" + email_host_password + "'\n"
                  "EMAIL_HOST_PORT = '" + email_host_port + "'\n"
                  "EMAIL_USE_TLS = " + email_use_tls + "\n"
                  "EMAIL_USE_SSL = " + email_use_ssl + "\n")
if email_use_ssl:
    file_custom.write("SESSION_COOKIE_SECURE = True\n"
                      "CSRF_COOKIE_SECURE = True\n")

authent_tablename = config.get("settings", "authent_tablename")
authent_database = config.get("settings", "authent_dbname")
authent_dbuser = config.get("settings", "authent_dbuser")
authent_engine = config.get("settings", "authent_engine")
file_custom.write("\n#\n"
                  "# External authent if required\n"
                  "# ..........................\n"
                  "AUTHENT_TABLENAME = '" + authent_tablename + "'\n"
                  "AUTHENT_DATABASE = '" + authent_database + "'\n")

if authent_tablename:
    file_custom.write("AUTHENTICATION_BACKENDS = ('geotrek.authent.backend.DatabaseBackend',)\n"
                      "DATABASES[AUTHENT_DATABASE] = {}\n"
                      "DATABASES[AUTHENT_DATABASE]['ENGINE'] = 'django.db.backends." + authent_engine + "'\n"
                      "DATABASES[AUTHENT_DATABASE]['NAME'] = '" + authent_database + "'\n"
                      "DATABASES[AUTHENT_DATABASE]['USER'] = '" + authent_dbuser + "'\n")


admins = config.get("settings", "mailadmins")
admins = admins.split(",")
managers = config.get("settings", "mailmanagers")
managers = managers.split(",")

file_custom.write("\n#\n"
                  "#  Email settings\n"
                  "# ..........................\n"
                  "ADMINS = (")
for mail_admin in admins:
    file_custom.write("('Admin " + title + "', '" + mail_admin + "'), ")
file_custom.write(")\n"
                  "MANAGERS = (")

for mail_manager in managers:
    file_custom.write("('Manager " + title + "', '" + mail_manager + "'), ")
file_custom.write(")\n")

mailalertsubject = config.get("settings", "mailalertsubject")
mailalertmessage = config.get("settings", "mailalertmessage")

file_custom.write("MAILALERTSUBJECT = '" + mailalertsubject + "'\n")

file_custom.write('MAILALERTMESSAGE = """' + mailalertmessage + '"""\n')

file_custom.close()
