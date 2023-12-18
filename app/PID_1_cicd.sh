#!/bin/bash

cd /dcsp/app/dcsp
python3 manage.py runserver 0.0.0.0:8000 &

# Black linter
echo Running Black linter
cd /dcsp/app
black . --line-length=79 --check

# Check the exit code of the linter
if [ $? -ne 0 ]; then
  echo "Black linter failed!"
  exit 1
fi

# Check for security issues with Bandit
echo "Checking for security issues"
cd /dcsp/app
bandit -c bandit.yml -r .

# Check the exit code of the linter
if [ $? -ne 0 ]; then
  echo "Bandit security checker failed!"
  exit 1
fi

# Run type checking using mypy (replace with your type-checking command)
echo "Running type checking..."
cd /dcsp/app
mypy /dcsp/app/dcsp/app/

# Check the exit code of the type checking command
if [ $? -ne 0 ]; then
  echo "Type checking failed!"
  exit 1
fi

# Run unit tests using pytest (replace with your unit testing command)
echo "Running unit tests..."
cd /dcsp/app/dcsp
python3 -u manage.py test --settings=dcsp.settings_tests --exclude-tag=git

# Check the exit code of the unit testing command
if [ $? -ne 0 ]; then
  echo "Unit testing failed!"
  exit 1
fi

# If all tests pass, the exit with 0
echo "Tests passed successfully!"
exit 0