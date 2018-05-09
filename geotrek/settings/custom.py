import os

# ALLOWED_HOST -> authorize domain for django app

ALLOWED_HOST = os.getenv('ALLOWED_HOST').split(',')

# SRID is used for geometric columns. Fixed at install, don't change it after

SRID = 2154

# DEFAULT_STRUCTURE_NAME -> Name for your default structure. Can be changed in geotrek admin interface

DEFAULT_STRUCTURE_NAME = 'GEOTEAM'

# ADMINS -> used to send error mails

# ADMINS = (
#     ('admin1', 'admin1@geotrek.fr'), # change with tuple ('your name', 'your@address.mail')
# )

# MANAGERS is used to send report mail

# MANAGERS = (
#     ('manager1', 'manager1@geotrek.fr'), # change with tuple ('your name', 'your@address.mail')
# )

# TIME_ZONE -> set your timezone for date format. For france, uncomment line beside
# For other zones : find it in https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

# TIME_ZONE=Europe/Paris


# MAIL SETTINGS
#
# DEFAULT_FROM_EMAIL =
# SERVER_EMAIL = DEFAULT_FROM_EMAIL
# EMAIL_HOST =
# EMAIL_HOST_USER =
# EMAIL_HOST_PASSWORD =
# EMAIL_HOST_PORT =
# EMAIL_USE_TLS = FALSE
# EMAIL_USE_SSL = FALSE

#
# External authent if required
# ..........................

# AUTHENT_DATABASE = 'your_authent_dbname'
# AUTHENT_TABLENAME = 'your_authent_table_name'
# if AUTHENT_TABLENAME:
#     AUTHENTICATION_BACKENDS = ('geotrek.authent.backend.DatabaseBackend',)
