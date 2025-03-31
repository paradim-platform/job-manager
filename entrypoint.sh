#!/bin/sh
# set -e

# Wait for the database to be ready before migrating
if [ -n "$DATABASE_HOST" ]; then
  >&2 echo "Waiting for database connection on $DATABASE_HOST:$DATABASE_PORT"
  until nc -z "$DATABASE_HOST" "$DATABASE_PORT"
  do
    >&2 echo "Waiting for database connection..."
    sleep 1
  done
  >&2 echo "Waiting for database connection... Done"
fi

python manage.py migrate --noinput
python manage.py createcachetable
python manage.py createsuperuser --noinput


exec "$@"