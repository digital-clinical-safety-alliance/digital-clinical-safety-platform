# The CICD pipeline

## The following testing is carried out
The following tests are carried out before the production environment will allow updated code.

1. Checks all of the necessary enviromental variables have been set.
2. Python code linter via Black linter.
3. Security scan via Bandit.
4. Python type hint check via mypy.
5. Python unit testing via Django's in built tester.
6. Coverage test, needs to be 100% to pass.
7. Template linter check via djLint
8. Push to main branch and then deply to production and create Github pages.

Integration testing needs to be added. This will likely be via Selenium.