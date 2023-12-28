#!/bin/bash

trap 'exitFunction' EXIT

exitFunction() {
    exit 0
}

cd /dcsp/app
python3 env_startup_check.py

# Check the exit code of env checker
if [ $? -ne 0 ]; then
  exit 1
fi


cd /dcsp/app/dcsp
#python3 manage.py runserver 0.0.0.0:8000 &
#gunicorn dcsp.wsgi:application -b 0.0.0.0:8000 &
gunicorn -c gunicorn_config_dev.py

while :
do
    ((count++))
    sleep 1
done