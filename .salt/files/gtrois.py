import os
{% set cfg = salt['mc_utils.json_load'](data) %}
{% set ddata = cfg.data %}
DATABASE = {
    'NAME': '{{ddata.db_name}}',                 
    'USER': '{{ddata.db_user}}',                 
    'PASSWORD': '{{ddata.db_pass}}',       
    'HOST': '{{ddata.db_host}}}}',                    
    'PORT': '{{ddata.db_port}}',                   
}

FTP = {
    'HOST': '{{ddata.gtrois.ftp_host}}',
    'USER': '{{ddata.gtrois.ftp_user}}',
    'PASSWORD': '{{ddata.gtrois.ftp_pass}}'
}

XML_PATH = '{{ddata.gtrois.xml_path}}'
DOC_PATH = '{{cfg.project_root}}/var/media/upload/paperclip/'

POI_FILE = 'points_interet.xml'
POI_DOCS_FILE = 'points_interet_documents.xml'
ITI_FILE = 'itineraires.xml'
ITI_DOCS_FILE = 'itineraires_documents.xml'

XML_BASE_DIR = '.'
POI_DOCS_DIR = 'POI_docs'
ITI_DOCS_DIR = 'ITI_docs'

FILES_LIST = {
    POI_FILE,
    POI_DOCS_FILE,
    ITI_FILE,
    ITI_DOCS_FILE
}

SRID=2154

ITI_SHP_PATH = os.path.join(XML_PATH, 'itineraires_geom.shp')

IGN_WEBSITE = "http://loisirs.ign.fr/catalogsearch/result/?q="
