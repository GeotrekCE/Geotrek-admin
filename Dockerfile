FROM ubuntu:bionic
#MAINTAINER Makina corpus "contact@geotrek.fr"

ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND=noninteractive

RUN mkdir -p /app/src/requirements

RUN apt-get update && apt-get upgrade -y -qq
ADD requirements/apt.txt /app/src/requirements/apt.txt
RUN apt-get install $(grep -vE "^\s*#" /app/requirements/apt.txt | tr "\n" " ") -y -qq
RUN apt-get clean all && apt-get autoclean
RUN locale-gen en_US.UTF-8
RUN wget https://bootstrap.pypa.io/get-pip.py && python get-pip.py && rm get-pip.py
RUN pip install pip==10.0.1 setuptools==39.1.0 wheel==0.31.0 virtualenv --upgrade
RUN useradd -ms /bin/bash django --uid 1000
RUN chown django:django -R /app

USER django

RUN mkdir -p /app/src/public/static /app/src/public/media /app/src/public/data
RUN mkdir -p /app/src/private/cache /app/src/private/log /app/src/private/templates /app/src/private/locale /app/src/private/static

ADD geotrek /app/src/geotrek
ADD manage.py /app/src/manage.py
ADD bulkimport /app/src/bulkimport
ADD VERSION /app/VERSION
ADD .coveragerc /app/src/.coveragerc
RUN virtualenv /app/venv
ADD requirements/pip.txt /app/src/requirements/pip.txt
RUN /app/venv/bin/pip install --no-cache-dir -r /app/src/requirements/pip.txt
ADD docker /app/src/docker

WORKDIR /app/src

EXPOSE 8000
CMD /app/venv/bin/gunicorn geotrek.wsgi:application -w 9 --bind 0.0.0.0:8000