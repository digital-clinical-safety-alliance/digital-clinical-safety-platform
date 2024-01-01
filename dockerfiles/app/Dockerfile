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

# TODO #35 - might have to check that removing admin privaleges does not affect creating volumes and networks
#RUN adduser -D dcsp-user

#COPY --from=builder --chown=dcsp-user:dcsp-user /dcsp

#RUN addgroup dcsp-user && adduser -DH -G dcsp-user dcsp-user

#RUN addgroup -S dcsp-user-group
#RUN adduser -S -D -h /usr/app/src dcsp-user dcsp-user-group
#RUN chown -R dcsp-user:dcsp-user-roup /dcsp
#RUN chmod -R 777 /dcsp

# Create a user group 'xyzgroup'
#RUN addgroup -S xyzgroup

# Create a user 'appuser' under 'xyzgroup'
#RUN adduser -S -D -h /usr/app/src appuser xyzgroup

# Chown all the files to the app user.
RUN useradd dcspuser
RUN chown -R dcspuser /dcsp
USER dcspuser 

