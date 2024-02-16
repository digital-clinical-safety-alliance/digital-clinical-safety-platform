#!/bin/bash

echo "--- Makemigrat ---"
cd /dcsp/app/dcsp
python3 manage.py makemigrations

if [ $? -ne 0 ]; then
  exit 1
fi

python3 manage.py makemigrations app

if [ $? -ne 0 ]; then
  exit 1
fi

echo "--- Migrate ---"
python3 manage.py migrate

if [ $? -ne 0 ]; then
  exit 1
fi

echo "--- Stopping Gunvicorn (if running) ---\n"
pkill -9 -f gunicorn

echo "--- Restarting Gunvicorn ---\n"
gunicorn -c gunicorn_config_dev.py &

if [ $? -ne 0 ]; then
  echo "--- Error with restarting Gunvicorn ---\n"
  exit 1
fi

echo "--- MMR.sh successfully ran ---\n"