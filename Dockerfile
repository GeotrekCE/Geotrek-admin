FROM ubuntu:xenial
RUN apt-get update
RUN apt-get install -y -q \
    build-essential python python-dev python-virtualenv \
    language-pack-en-base language-pack-fr-base gettext \
    libpq-dev libgdal-dev libproj-dev libxml2-dev libxslt-dev \
    libcairo2 libpango1.0-0 libgdk-pixbuf2.0-dev libffi-dev
RUN apt-get clean
RUN useradd -ms /bin/bash django
USER django
WORKDIR /home/django
RUN mkdir -p var/log
RUN virtualenv env
RUN ./env/bin/pip install --upgrade pip==9.0.3 setuptools==39.0.1
RUN ./env/bin/pip install --global-option=build_ext --global-option="-I/usr/include/gdal/" gdal==1.11.2
ADD requirements.txt ./
RUN ./env/bin/pip install -r requirements.txt
ADD .flake8 manage.py README.rst setup.py VERSION ./
ADD geotrek/settings/custom.py.dist geotrek/settings/custom.py
ADD docs/changelog.rst docs/
ADD geotrek/ geotrek/
RUN ./env/bin/python manage.py collectstatic --noinput
