FROM makinacorpus/geodjango:bionic-3.6

ENV DJANGO_SETTINGS_MODULE geotrek.settings.prod
# SET LOCAL_UID, help to use in dev
ARG LOCAL_UID=1000
# Add default SECRET KEY / used for compilemessages
ENV SECRET_KEY temp
# default gunicorn options
ENV GUNICORN_CMD_ARGS="--bind 0.0.0.0:8000 --workers 5 --timeout 600"
# Add default path for log / used for compilemessages
RUN mkdir -p /app/src/var/log

# install postgis without dependencies to get raster2pgsql command
RUN apt-get update && apt-get install -y \
    unzip \
    sudo \
    less \
    nano \
    curl \
    git \
    gosu \
    software-properties-common \
    shared-mime-info \
    fonts-liberation \
    libfreetype6-dev \
    libxml2-dev \
    libxslt-dev \
    libcairo2 \
    libpango1.0-0 \
    libgdk-pixbuf2.0-dev \
    libffi-dev &&\
    apt-get --no-install-recommends install postgis -y && \
    apt-get clean all && rm -rf /var/lib/apt/lists/* && rm -rf /var/cache/apt/*

RUN useradd -ms /bin/bash django --uid $LOCAL_UID
ADD geotrek /app/src/geotrek
ADD manage.py /app/src/manage.py
ADD bulkimport /app/src/bulkimport
ADD VERSION /app/src/VERSION
ADD .coveragerc /app/src/.coveragerc
RUN chown django:django -R /app
COPY docker/* /usr/local/bin/

ADD requirements.txt /app/src/requirements.txt
RUN pip3 install --no-cache-dir -r /app/src/requirements.txt

USER django

WORKDIR /app/src
# persists compiled locales
RUN ./manage.py compilemessages

EXPOSE 8000

USER root

ENTRYPOINT ["/bin/sh", "-e", "/usr/local/bin/entrypoint.sh"]

CMD ["/bin/sh", "-e", "/usr/local/bin/run.sh"]
