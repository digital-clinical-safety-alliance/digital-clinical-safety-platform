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

echo "Starting up Gunicorn server for Django"
cd /dcsp/app/dcsp
gunicorn -c gunicorn_config_dev.py &

echo "Gunicorn running. PID_1.sh on loop"

while :
do
    ((count++))
    sleep 1
done