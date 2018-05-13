FROM ubuntu:bionic
#MAINTAINER Makina Corpus "contact@geotrek.fr"

ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND noninteractive
ENV DJANGO_SETTINGS_MODULE geotrek.settings.prod
ARG LOCAL_UID=1000
RUN mkdir -p /app/src

RUN apt-get update && apt-get upgrade -y -qq
RUN apt-get install -y -qq unzip wget sudo less nano curl language-pack-en-base git gettext python python-dev \
software-properties-common build-essential gdal-bin binutils libproj-dev libxml2-dev libxslt-dev libcairo2 \
libpango1.0-0 libgdk-pixbuf2.0-dev libffi-dev shared-mime-info libpq-dev libgdal-dev libfreetype6-dev fonts-liberation
RUN apt-get clean all && apt-get autoclean
RUN locale-gen en_US.UTF-8
RUN wget https://bootstrap.pypa.io/get-pip.py && python get-pip.py && rm get-pip.py
RUN pip install pip==10.0.1 setuptools==39.1.0 wheel==0.31.0 virtualenv --upgrade
RUN useradd -ms /bin/bash django --uid $LOCAL_UID
RUN mkdir -p /app/src/var/static /app/src/var/extra_static /app/src/var/media /app/src/var/data /app/src/var/cache /app/src/var/log /app/src/var/extra_templates /app/src/var/extra_locale
ADD geotrek /app/src/geotrek
ADD manage.py /app/src/manage.py
ADD bulkimport /app/src/bulkimport
ADD VERSION /app/src/VERSION
ADD .coveragerc /app/src/.coveragerc
RUN chown django:django -R /app

USER django

RUN virtualenv /app/venv
ADD requirements.txt /app/src/requirements.txt
RUN /app/venv/bin/pip install --no-cache-dir -r /app/src/requirements.txt
# force leaflet version
ADD docker /app/src/docker

WORKDIR /app/src

EXPOSE 8000
CMD /app/venv/bin/gunicorn geotrek.wsgi:application -w 9 --bind 0.0.0.0:8000