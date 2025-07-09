# How to install the DCSP app on a local instance

## Prerequisites

* A computer with resources that can manage a docker container running a web app
* Docker
* A text editor
* A command line interface

## Installing

There are three separate docker-compose files to chose from. There are development, CICD pipeline for testing purposes and also a production docker-compose files. These are called:

* docker-compose-dev.yml
* docker-compose-cicd.yml
* docker-compose-prod.yml

The docker container

* docker-compose-prod-certbot.yml

is used only once when initially setting up the production environment on a new production server.

### Development environment

* Clone the repository from https://github.com/digital-clinical-safety-alliance/digital-clinical-safety-platform.
* `cd` into the root folder of the repository.
* Copy, paste and rename the .env_example to .env_dev
* Edit the environment file as needed
* Run the below command

```$ docker compose -f docker-compose-dev.yml up```

And then

```docker compose -f docker-compose-dev.yml exec -it dcsp-docs-builder-dev python3 dcsp/manage.py migrate```

And then

```docker compose -f docker-compose-dev.yml exec -it dcsp-docs-builder-dev python3 dcsp/manage.py createsuperuser```

* You should be up and running.
* Use can use the below command to open a command line within the main container

```$ docker exec -it dcsp-docs-builder-dev bash```

### CICD environment

* You should not routinely need to run the CICD environment on your devlopment environment, but you may wish to for testing before using GitHub actions.
* Clone the repository from https://github.com/digital-clinical-safety-alliance/digital-clinical-safety-platform (if not already done)
* `cd` into the root folder of the repository.
* Copy, paste and rename the .env_example to .env_cicd
* Edit the environment file as needed
* Run the below command

```$ docker compose -f docker-compose-cicd.yml up```

* You should be up and running.
* Use the below command to open a command line within the main container

```$ docker exec -it dcsp-docs-builder-cicd bash```

### Development environment

* Clone the repository from https://github.com/digital-clinical-safety-alliance/digital-clinical-safety-platform (if not already done).
* `cd` into the root folder of the repository.
* Copy, paste and rename the .env_example to .env_prod
* Edit the environment file as needed
* Run the below command to get your first certbot certificate from letsencrypt

```$ docker compose -f docker-compose-prod-certbot.yml up```

* Next, run the below command

```$ docker compose -f docker-compose-prod.yml up```

* Use the below command to open a command line within the main container

```$ docker exec -it dcsp-docs-builder-prod bash```

* Edit the cron daemon file (this can be done with crontab -e which normally opens a Vim instance).
* Add the below job to the file

    0 0,12 * * * cd /src/digital-clinical-safety-platform && sh crontab-certbot.sh

* And that should be the production site up and running