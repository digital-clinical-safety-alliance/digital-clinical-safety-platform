#TODO: need to pin down ubuntu version
FROM ubuntu:latest as base
WORKDIR /dcsp

# NB: Need to create identical group and user on the production site
# user and group 1001 enables access on github actions
ARG UNAME=dcspuser
ARG FOLDER=/dcsp
ARG FOLDER_PROJECTS=/projects
ARG FOLDER_DOCUMENTATION_PAGES=/documentation-pages
ARG TEST_FOLDER=/test_folder
ARG UID=1001
ARG GID=1001

#TODO: may need to remove update as this will have different updates over time
#TODO: do we need upgrade as well for security?
RUN apt-get -y update
RUN apt-get -y upgrade
COPY packages.txt /dcsp
RUN xargs apt-get -y install <packages.txt

COPY requirements-base.txt /dcsp
RUN pip install -r requirements-base.txt

#COPY requirements-dev-cicd.txt /dcsp

# Copy modified files across to utilise "Hazard" headings in docstrings
COPY mkdocs_overwrite.py /dcsp
COPY overwrites/ /dcsp/overwrites/
RUN python3 mkdocs_overwrite.py

# Chown all the files to user.
RUN groupadd -g $GID -o $UNAME
RUN useradd -m -u $UID -g $GID -o -s /bin/bash $UNAME
RUN chown -R $UNAME $FOLDER
RUN chmod -R g+rw $FOLDER

RUN mkdir -p $FOLDER_PROJECTS
# VOLUME $FOLDER_PROJECTS
RUN chown -R $UNAME $FOLDER_PROJECTS
RUN chmod -R g+rw $FOLDER_PROJECTS

RUN mkdir -p $FOLDER_DOCUMENTATION_PAGES
# VOLUME $FOLDER_DOCUMENTATION_PAGES
RUN chown -R $UNAME $FOLDER_DOCUMENTATION_PAGES
RUN chmod -R g+rw $FOLDER_DOCUMENTATION_PAGES

RUN mkdir -p /test_folder
# VOLUME $FOLDER_DOCUMENTATION_PAGES
RUN chown -R $UNAME /test_folder
RUN chmod -R g+rw /test_folder

# run 'pip freeze' without node, as node adds 3 files which 'pip install' 
# cannot install

FROM base as dev
#RUN pip install -r requirements-dev-cicd.txt
#WORKDIR /dcsp/cicd/node
#RUN apt-get -y install nodejs npm
# RUN npm install --save-dev jest jsdom

FROM dev as cicd
#RUN pip install -r requirements-dev-cicd.txt
#RUN apt-get -y install nodejs npm
USER $UNAME

FROM base as prod
USER $UNAME


