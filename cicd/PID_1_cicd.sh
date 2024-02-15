#!/bin/bash


COVERAGE_THRESHOLD=90

echo "Environmental variables check"
echo "-----------------------------"

cd /dcsp/app
python3 env_startup_check.py

# Check the exit code of env checker
if [ $? -ne 0 ]; then
  exit 1
fi

# Black linter
echo Running Black linter
echo "-------------------"
cd /dcsp/cicd/black_linter

if [ "$FORMAT" = "True" ]; then
    python3 -m black --config pyproject.toml /dcsp/    
fi

python3 -m black --config pyproject.toml /dcsp/ --check

# Check the exit code of the linter
if [ $? -ne 0 ]; then
  echo "Black linter failed!"
  exit 1
fi

# Check for security issues with Bandit
echo "Checking for security issues"
echo "----------------------------"
cd /dcsp/cicd/
bandit -c bandit.yml -r /dcsp/app/ 

# Check the exit code of the linter
if [ $? -ne 0 ]; then
  echo "Bandit security checker failed!"
  exit 1
fi

# Run type checking using mypy
echo "Running type checking"
echo "---------------------"
cd /dcsp/cicd
mypy /dcsp/app/dcsp/app/

# Check the exit code of the type checking command
if [ $? -ne 0 ]; then
  echo "Type checking failed!"
  exit 1
fi

# Run unit tests using pytest
echo "Running unit tests"
echo "------------------"
cd /dcsp/app/dcsp
coverage run --rcfile=/dcsp/cicd/coverage.ini manage.py test --settings=dcsp.settings_tests --exclude-tag=git

# Check the exit code of the unit testing command
if [ $? -ne 0 ]; then
  echo "Unit testing failed!"
  exit 1
fi

echo "Coverage Report"
echo "---------------"
COVERAGE_PERCENTAGE=$(coverage report -m | grep "TOTAL" | awk '{print $4}' | tr -d %)
echo "Coverage Percentage: $COVERAGE_PERCENTAGE%"
echo ""
coverage report -m

# Check the exit code of the coverage report
#if [ "$COVERAGE_PERCENTAGE" -lt "$COVERAGE_THRESHOLD" ]
#  then
#    echo "Coverage failed: actual $COVERAGE_PERCENTAGE, threshold $COVERAGE_THRESHOLD"
#    exit 1
#fi


echo "HTML template linting with djLint"
echo "---------------"
cd /dcsp/cicd/djlint
djlint /dcsp/app/dcsp/app/templates --lint

if [ $? -ne 0 ]; then
  echo "HTML template linting via djLint failed!"
  exit 1
fi

# If all tests pass, the exit with 0
echo "Tests passed successfully!"
exit 0