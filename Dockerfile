FROM makinacorpus/geodjango:bionic-py2

ENV DJANGO_SETTINGS_MODULE geotrek.settings.prod
ARG LOCAL_UID=1000
RUN mkdir -p /app/src

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