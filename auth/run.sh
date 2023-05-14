#! /usr/bin/env sh
set -e
cd app && alembic upgrade head && cd ..
exec gunicorn --workers 1 --bind 0.0.0.0:5000 wsgi_app:app