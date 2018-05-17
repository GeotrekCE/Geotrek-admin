#!/usr/bin/env bash

cd /app/src

exec gosu django "$@"