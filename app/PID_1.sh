#!/bin/bash

trap printout EXIT

exitFunction() {
    exit
}

cd /dcsp/app/dcsp
python3 manage.py runserver 0.0.0.0:8000 &

#cd /dcsp/mkdocs
#mkdocs serve &

while :
do
    ((count++))
    sleep 1
done