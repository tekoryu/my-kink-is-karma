#!/bin/sh

docker-compose run --rm app sh -c "python manage.py collectstatic --noinput"
python manage.py createsuperuser --username="tekoryu" --email="chedou@gmail.com" --noinput