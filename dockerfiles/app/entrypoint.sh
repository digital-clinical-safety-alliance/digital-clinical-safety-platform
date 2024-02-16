#!/bin/bash
UNAME=dcspuser
FOLDER=/dcsp
FOLDER_PROJECTS=/projects
FOLDER_DOCUMENTATION_PAGES=/documentation-pages
UID=1001
GID=1001

chown -R $UNAME:$GID $FOLDER_PROJECTS
chmod -R g+rw $FOLDER_PROJECTS
chown -R $UNAME:$GID $FOLDER_DOCUMENTATION_PAGES
chmod -R g+rw $FOLDER_DOCUMENTATION_PAGES
# Then, switch to the non-root user and start the main process of your container:
echo Hi there! I am $UNAME
exec gosu $UNAME "$@"