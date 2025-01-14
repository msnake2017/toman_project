#!/bin/bash

set -e

python manage.py collectstatic --noinput
python manage.py migrate
gunicorn --bind 0.0.0.0:8000 --workers=4 toman_shop.wsgi:application
