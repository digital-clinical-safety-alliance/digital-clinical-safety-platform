#!/bin/bash

# Black linter
echo "----------------------"
echo " Running Black linter "
echo "----------------------"

cd /dcsp/cicd/black_linter
python3 -m black --config pyproject.toml /dcsp/