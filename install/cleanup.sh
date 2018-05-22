#!/usr/bin/env bash

docker-compose run web ./manage.py clearsessions
docker-compose run web ./manage.py thumbnail_cleanup
