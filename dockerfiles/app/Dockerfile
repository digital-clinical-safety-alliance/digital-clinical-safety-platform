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

# Create user
RUN addgroup --system dcsp-user && adduser --system --group dcsp-user

# Change to dcsp-user user
USER dcsp-user

