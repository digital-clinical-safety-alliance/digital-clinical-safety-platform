#TODO: need to pin down ubuntu version
FROM ubuntu:latest 
WORKDIR /dcsp
COPY requirements.txt /dcsp
COPY packages.txt /dcsp
#TODO: may need to remove update as this will have different updates over time
#TODO: do we need upgrade as well for security?
RUN apt-get update

RUN xargs apt-get -y install <packages.txt

RUN pip install -r requirements.txt

