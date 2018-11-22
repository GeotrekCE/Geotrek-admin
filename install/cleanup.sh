#!/usr/bin/env bash

sudo docker-compose run web ./manage.py clearsessions
sudo docker-compose run web ./manage.py thumbnail_cleanup
