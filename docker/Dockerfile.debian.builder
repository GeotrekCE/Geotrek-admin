ARG DISTRO=ubuntu:focal

FROM ${DISTRO} AS base


RUN apt-get update -qq -o Acquire::Languages=none && \
    env DEBIAN_FRONTEND=noninteractive apt-get install -yqq lsb-release && \
    if test "$(lsb_release -cs)" = 'focal' ; then \
       env DEBIAN_FRONTEND=noninteractive apt-get install -yqq software-properties-common; \
       add-apt-repository ppa:deadsnakes/ppa; \
       add-apt-repository ppa:jyrki-pulliainen/dh-virtualenv; fi &&\
    env DEBIAN_FRONTEND=noninteractive apt-get install -yqq \
    nano \
    dpkg-dev \
    debhelper \
    dh-virtualenv \
    git \
    devscripts \
    equivs


WORKDIR /dpkg-build

FROM base AS builder

COPY debian ./debian

RUN env DEBIAN_FRONTEND=noninteractive mk-build-deps --install --tool='apt-get -o Debug::pkgProblemResolver=yes --no-install-recommends --yes' debian/control

COPY geotrek ./geotrek
COPY conf ./conf
COPY setup.py ./setup.py
COPY requirements.txt ./requirements.txt
COPY VERSION ./VERSION
COPY manage.py ./manage.py
COPY MANIFEST.in ./MANIFEST.in

RUN if test "$(lsb_release -cs)" = 'noble' ; then \
      sed -i 's/python3.10/python3.12/g' debian/rules; \
    fi

RUN sed -i -re "1s/..UNRELEASED/.ubuntu$(lsb_release -rs)) $(lsb_release -cs)/" debian/changelog \
    && chmod a-x debian/geotrek.*
RUN django-admin compilemessages
RUN dpkg-buildpackage -us -uc -b
RUN mkdir -p /dpkg && cp -pl /geotrek[-_]* /dpkg
RUN dpkg-deb -I /dpkg/geotrek*.deb

WORKDIR /dpkg
