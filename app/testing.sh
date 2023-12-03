#!/bin/bash

start=`date +%s`

# Typing checking
#echo TYPE CHECKING
#echo Checking functions folder...
#mypy /dcsp/app/dcsp/app/functions

#echo Checking view.py...
#mypy /dcsp/app/dcsp/app/views.py

#echo NB: Need to add more files to type check from Django app!

#echo UNIT TESTING
#echo Django and unittest...
cd /dcsp/app/dcsp/
python3 manage.py test #-v 0

end=`date +%s`

#echo Complete - execution time was `expr $end - $start` seconds.