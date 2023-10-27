#TODO: need to pin down ubuntu version
FROM ubuntu:latest 
WORKDIR /
COPY requirements.txt /
COPY packages.txt /
#TODO: may need to remove update as this will different updates over time
RUN apt-get update

RUN xargs apt-get -y install <packages.txt

RUN pip install -r requirements.txt

