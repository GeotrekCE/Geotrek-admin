FROM ubuntu:xenial
RUN apt-get update
RUN apt-get install -y -q \
    build-essential python3 python3-dev python3-venv git \
    language-pack-en-base language-pack-fr-base gettext \
    libpq-dev libgdal-dev libproj-dev libxml2-dev libxslt-dev \
    libcairo2 libpango1.0-0 libgdk-pixbuf2.0-dev libffi-dev \
    postgresql-client
RUN apt-get clean
RUN useradd -ms /bin/bash django
USER django
WORKDIR /home/django
RUN mkdir -p var/log
RUN python3 -m venv env
RUN ./env/bin/pip3 install --upgrade pip==9.0.3 setuptools==39.0.1
RUN ./env/bin/pip3 install --global-option=build_ext --global-option="-I/usr/include/gdal/" gdal==1.11.2
ADD requirements.txt ./
ADD editable.txt ./
RUN ./env/bin/pip3 install -r requirements.txt
RUN ./env/bin/pip3 install -r editable.txt
ADD .flake8 manage.py README.rst setup.py VERSION ./
ADD geotrek/settings/custom.py.dist geotrek/settings/custom.py
ADD docs/changelog.rst docs/
ADD geotrek/ geotrek/
RUN ./env/bin/python3 manage.py collectstatic --noinput
RUN export DJANGO_SETTINGS_MODULE=geotrek.settings.base
RUN export LANG=en_US.UTF-8
