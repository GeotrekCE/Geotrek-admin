#!/usr/bin/env bash

docker pull $DOCKER_TEST_REPO:$TRAVIS_BUILD_NUMBER

echo "$DOCKER_PASSWORD" | docker login --username "$DOCKER_LOGIN" --password-stdin

docker tag $DOCKER_TEST_REPO:$TRAVIS_BUILD_NUMBER geotrekce/admin:$GEOTREK_VERSION
docker push geotrekce/admin:$GEOTREK_VERSION;

if [[ $GEOTREK_VERSION != *.dev* ]];
then
    docker tag $DOCKER_TEST_REPO:$TRAVIS_BUILD_NUMBER geotrekce/admin:latest;
    docker push geotrekce/admin:latest;
fi
