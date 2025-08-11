#!/bin/sh

python manage.py makemigrations
python manage.py migrate

python manage.py example_data
python manage.py runserver 0.0.0.0:8000
