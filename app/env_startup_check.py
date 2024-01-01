"""Checks to see if all the environmental variables have been set

"""
# TODO #31 does this code need unit testing as well?
import os
import sys

env_to_check: list[str] = [
    "DJANGO_SECRET_KEY",
    "ALLOW_HOSTS",
    "DJANGO_SECRET_KEY",
    "ALLOW_HOSTS",
    "DEBUG",
    "EMAIL_HOST_USER",
    "EMAIL_HOST_PASSWORD",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "POSTGRES_DB",
    "POSTGRES_ENGINE",
    "POSTGRES_PORT",
]

env_to_check_dict: dict[str, str] = {}
exit_code: int = 0

for env in env_to_check:
    value = os.getenv(env, "")

    if value != "":
        env_to_check_dict[env] = "set"
    else:
        env_to_check_dict[env] = "NOT set"
        exit_code = 1

print("ENV CHECKER - ", end="")
if exit_code == 0:
    print("All variables are set\n")
else:
    print("Error with environmental variables\n")
    print("Please see below which environmental variables are not set:\n")
    for key, value in env_to_check_dict.items():
        print(f"{ key } - { value }")

sys.exit(exit_code)
