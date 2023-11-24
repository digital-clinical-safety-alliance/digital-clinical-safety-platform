#!/bin/bash

# A sh script is used to better manage child processes
# and stop zombies being created

cd /cshd/mkdocs
mkdocs serve 
#> /dev/null 2>&1