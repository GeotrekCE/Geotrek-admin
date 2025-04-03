ARG BASE_IMAGE=ubuntu:noble

FROM ${BASE_IMAGE} AS base

# add labels
LABEL org.opencontainers.image.authors="Makina Corpus"
LABEL org.opencontainers.image.source="https://github.com/GeotrekCE/Geotrek-admin/"
LABEL org.opencontainers.image.documentation="https://geotrek.readthedocs.io/"
LABEL org.opencontainers.image.vendor="Makina Corpus"
LABEL org.opencontainers.image.licenses="BSD-2-Clause"
LABEL org.opencontainers.image.url="https://geotrek.fr"
LABEL org.opencontainers.image.title="Geotrek-admin"
LABEL org.opencontainers.image.description="Manage and promote your trails and tourist content and activities."

ENV PYTHONBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive
ENV ENV=prod
ENV SERVER_NAME="localhost"
ENV POSTGRES_HOST="host.docker.internal"
ENV POSTGRES_PORT="5432"
ENV POSTGRES_USER="geotrek"
ENV POSTGRES_DB="geotrekdb"
ENV REDIS_HOST="redis"
ENV CONVERSION_HOST="convertit"
ENV CAPTURE_HOST="screamshotter"
ENV CUSTOM_SETTINGS_FILE="/opt/geotrek-admin/var/conf/custom.py"
ENV TZ=UTC

WORKDIR /opt/geotrek-admin
RUN mkdir -p /opt/geotrek-admin/var/log /opt/geotrek-admin/var/cache
RUN useradd -m -d /opt/geotrek-admin -s /bin/false geotrek && chown geotrek:geotrek -R /opt

# Install postgis because raster2pgsl is required by manage.py loaddem
RUN apt-get update -qq && apt-get install -y -qq  \
    python3 \
    ca-certificates \
    gettext \
    postgresql-client \
    tzdata \
    gdal-bin \
    binutils \
    libproj-dev \
    unzip \
    less \
    iproute2 \
    nano \
    curl \
    software-properties-common \
    shared-mime-info \
    libmagic1 \
    fonts-liberation \
    libssl-dev \
    libfreetype6-dev \
    libxml2-dev \
    libxslt-dev \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-dev \
    libffi-dev \
    fonts-dejavu-core \
    libvips && \
    apt-get install -y --no-install-recommends postgis && \
    apt-get clean all && rm -rf /var/lib/apt/lists/* && rm -rf /var/cache/apt/*

USER geotrek
COPY --chown=geotrek:geotrek docker/scripts/* /usr/local/bin/
ENTRYPOINT ["/bin/sh", "-e", "/usr/local/bin/entrypoint.sh"]
EXPOSE 8000

FROM base AS build

USER root

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update -qq && apt-get install -y -qq  \
    git \
    python3-dev \
    python3-venv \
    build-essential \
    graphviz \
    libpq-dev &&\
    apt-get clean all && rm -rf /var/lib/apt/lists/* && rm -rf /var/cache/apt/*

USER geotrek
RUN uv venv /opt/venv
COPY requirements.txt requirements.txt
ENV UV_PYTHON=/opt/venv/bin/python

RUN uv pip install --no-cache-dir -r requirements.txt

FROM build AS dev

ENV ENV=dev
COPY requirements-dev.txt requirements-dev.txt
RUN uv pip install --no-cache-dir -r requirements-dev.txt
COPY ./docs/requirements.txt doc-requirements.txt
RUN uv pip install --no-cache-dir -r doc-requirements.txt

CMD ["./manage.py", "runserver", "0.0.0.0:8000"]

FROM base AS prod

COPY --chown=geotrek:geotrek --from=build /opt/venv /opt/venv
COPY --chown=geotrek:geotrek geotrek/ geotrek/
COPY --chown=geotrek:geotrek manage.py manage.py
COPY --chown=geotrek:geotrek VERSION VERSION
COPY --chown=geotrek:geotrek setup.cfg setup.cfg

RUN CUSTOM_SETTINGS_FILE= SECRET_KEY=tmp /opt/venv/bin/python ./manage.py compilemessages

USER root

RUN apt-get update -qq && apt-get -yqq full-upgrade && \
    apt-get clean all && rm -rf /var/lib/apt/lists/* && rm -rf /var/cache/apt/*

USER geotrek

CMD ["gunicorn", "geotrek.wsgi:application", "--bind=0.0.0.0:8000"]
