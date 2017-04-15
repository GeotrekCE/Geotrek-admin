from fabric.api import *
from fabtools import *
import fabtools
import ConfigParser
from  os import path,unlink,getcwd
import tempfile
import datetime


#we work in relative path 
workingdir=getcwd()
settingsfile='etc/settings.ini'
settingssection='settings'

def migratesettings(sample, user):
	configSample = ConfigParser.ConfigParser()
	configUser = ConfigParser.ConfigParser()
	configSample.read(sample)

	if not files.is_file(user):
		#copie sample to user
		require.files.directory(path.dirname(user))
		require.files.file(user,source=sample)
		#we just copie sample, no need to compare
		return 1

	#check user settings with sample
	#reading previous config
	configUser.read(user)
	#openning file to update
	f = open(user,'a')
	change=False
	#copy into user missing section/option
	for section in configSample.sections():
		if not configUser.has_section(section):
			print("Section '%(section)s' is missing, aborting." % locals())
			return 2
		for option in configSample.options(section):
			if not configUser.has_option(section,option):
				print("Adding option: '%(option)s' in user file" % locals())
				f.write('#Added automatically on %s\n' % str(datetime.datetime.now()))
				f.write('%s = %s\n' % (option, configSample.get(section,option)))
				change=True

	f.close()
	if change:
		return 1
	return 0
	
def installpkg():
	##install package
	require.deb.ppa('ppa:ubuntugis/ubuntugis-unstable')
	require.deb.ppa('ppa:sharpie/postgis-stable')
	require.deb.packages([
		'python-software-properties',
		'unzip',
		'python-dev',
		'python-virtualenv',
		'gettext',
		'build-essential',
		'libjson0',
		'libgdal1',
		'libgdal-dev',
		'libproj0',
		'libgeos-c1',
		'gdal-bin',
		'postgis-bin',
		'postgresql-client',
		'libreoffice',
		'unoconv'
		])

def common():
	# install packages
	installpkg()
	
	#run ('make install')

	if migratesettings('conf/settings.ini.sample',settingsfile):
		print('Config file has been updated, please review.')
		print('Exiting')
		quit(5)

	#config db
	config = ConfigParser.ConfigParser()
	config.read(settingsfile)
	##ini value
	dbname=config.get(settingssection,'dbname')
	dbuser=config.get(settingssection,'dbuser')
	dbpassword=config.get(settingssection,'dbpassword')
	dbhost=config.get(settingssection,'dbhost')
	dbport=config.get(settingssection,'dbport')
	## database is local
	if(dbhost == 'localhost'):
		#setup postgres
		require.postgres.server()
		require.deb.package('postgresql-9.1-postgis2')
		#create db
		if not postgres.database_exists(dbname):
			require.postgres.database(dbname,dbuser)
			postgres.execute_statement('CREATE EXTENSION postgis;',dbname)
		#create user
		if not postgres.user_exists(dbuser):
			require.postgres.user(dbuser,dbpassword)
			postgres.execute_statement("GRANT ALL PRIVILEGES ON DATABASE %(dbname)s TO %(dbuser)s;" % locals())
			postgres.execute_statement("GRANT ALL ON spatial_ref_sys, geometry_columns, raster_columns TO '%(dbuser)s';" % locals(), dbname)
			if(files.is_file('/etc/postgresql/9.1/main/pg_hba.conf')):
				utils.run_as_root('cat << _EOF_ >> /etc/postgresql/9.1/main/pg_hba.conf \
# Automatically added by Caminae 	installation :\
local    ${dbname}     ${dbuser}                   md5\
_EOF_')
		print('If you want to listen to all interfaces, edit postgres database.')

	ret = postgres.check_connect(dbuser,dbpassword,dbname,dbhost,dbport)
	if not ret.return_code == 0:
		print("Failed to connect to database with settings provided in '" + settingsfile + "'." )
		print("Check your postgres configuration (pg_hba.conf) : it should allow md5 identification for user '" + dbuser + "' on databse '" + dbname + "'")
		quit(4)

@task
def deploy():
	with cd(workingdir):
		common()

		require.deb.packages(['nginx','yui-compressor'])
		run('make deploy')
		require.files.file('etc/settings',mode=0700)
		require.files.file('etc/settings',mode=0700)

		if files.is_file('etc/nginx.conf'):
			utils.run_as_root('rm /etc/nginx/sites-enabled/default')
			utils.run_as_root('cp etc/nginx.conf /etc/nginx/sites-available/caminae')
			utils.run_as_root('ln -sf /etc/nginx/sites-available/caminae /etc/nginx/sites-enabled/caminae')
			utils.run_as_root('cp etc/init/supervisor.conf /etc/init/supervisor.conf')
			service.restart('nginx')
			service.restart('supervisor')
		else:
			print('Caminae package could not be installed.')
			quit(6)

@task
def dev():
	print ('Not yet :(')
	quit()
	with cd(workingdir):
		common()
