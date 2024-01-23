#TODO: need to pin down ubuntu version
FROM ubuntu:latest 
WORKDIR /dcsp

#TODO: may need to remove update as this will have different updates over time
#TODO: do we need upgrade as well for security?
RUN apt-get update
COPY packages.txt /dcsp
RUN xargs apt-get -y install <packages.txt

COPY requirements.txt /dcsp
RUN pip install -r requirements.txt

# Copy modified files across to utilise "Harzard" headings in docstrings
#COPY ../../overwrites/requirements.txt /dcsp

# Chown all the files to user.
# NB: Need to create identical group and user on the production site
ARG UNAME=dcspuser
ARG FOLDER=/dcsp
ARG UID=1001
ARG GID=1001

RUN groupadd -g $GID -o $UNAME
RUN useradd -m -u $UID -g $GID -o -s /bin/bash $UNAME
RUN chown -R $UNAME $FOLDER
RUN chmod -R g+rw $FOLDER
#USER $UNAME

