FROM makinacorpus/geodjango:bionic-3.6

ENV ENV=prod
ENV ALLOWED_HOSTS="localhost"
# If POSTGRES_HOST is empty, entrypoint will set it to the IP of the docker host in the container
ENV POSTGRES_HOST=""
ENV POSTGRES_PORT="5432"
ENV POSTGRES_USER="geotrek"
ENV POSTGRES_PASSWORD="geotrek"
ENV POSTGRES_DB="geotrekdb"
ENV CUSTOM_SETTINGS_FILE="/app/src/var/conf/custom.py"

WORKDIR /app/src

# Install postgis because raster2pgsl is required by manage.py loaddem
RUN apt-get update && apt-get install -y \
    unzip \
    sudo \
    less \
    nano \
    curl \
    git \
    iproute2 \
    software-properties-common \
    shared-mime-info \
    fonts-liberation \
    libfreetype6-dev \
    libxml2-dev \
    libxslt-dev \
    libcairo2 \
    libpango1.0-0 \
    libgdk-pixbuf2.0-dev \
    libffi-dev && \
    apt-get install -y --no-install-recommends postgis && \
    apt-get clean all && rm -rf /var/lib/apt/lists/* && rm -rf /var/cache/apt/*

COPY requirements.txt requirements.txt
RUN python3 -m venv env
RUN env/bin/pip install --no-cache-dir -r requirements.txt

COPY geotrek/ geotrek/
COPY manage.py manage.py
COPY bulkimport/ bulkimport/
COPY VERSION VERSION
COPY .coveragerc .coveragerc
COPY docker/* /usr/local/bin/

RUN cd geotrek; ENV=dev CUSTOM_SETTINGS_FILE= SECRET_KEY=tmp ../env/bin/python ../manage.py compilemessages; cd ..
RUN ln -sf /app/src/var/conf/parsers.py /app/src/bulkimport/parsers.py

EXPOSE 8000
ENTRYPOINT ["/bin/sh", "-e", "/usr/local/bin/entrypoint.sh"]
CMD ["gunicorn", "geotrek.wsgi:application", "--bind=0.0.0.0:8000"]
