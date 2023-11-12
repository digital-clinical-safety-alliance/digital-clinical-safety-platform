#!/bin/bash

trap printout EXIT

exitFunction() {
    exit
}

cd /app/cshd
python3 manage.py runserver 0.0.0.0:8000 &

cd /mkdocs
mkdocs serve &

while :
do
    ((count++))
    sleep 1
done