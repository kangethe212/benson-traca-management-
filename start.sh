#!/bin/bash
export DJANGO_SETTINGS_MODULE=myproject.settings_production
python manage.py migrate --noinput
python manage.py collectstatic --noinput
gunicorn myproject.wsgi:application
