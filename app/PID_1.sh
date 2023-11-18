#!/bin/bash

trap printout EXIT

exitFunction() {
    exit
}

cd /cshd/app/cshd
python3 manage.py runserver 0.0.0.0:8000 &

#cd /cshd/mkdocs
#mkdocs serve &

while :
do
    ((count++))
    sleep 1
done