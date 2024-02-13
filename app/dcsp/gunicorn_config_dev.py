# gunicorn_config.py
import os
import glob
from fnmatch import fnmatch

import app.functions.constants as c


def find_html_files(
    folder_path: str,
) -> list[str]:
    """ """
    files_to_check = []

    for path, _, files in os.walk(folder_path):
        for name in files:
            if (
                fnmatch(name, "*.html")
                or fnmatch(name, "*.md")
                or fnmatch(name, "*.js")
            ):
                files_to_check.append(os.path.join(path, name))

    return files_to_check


# The address and port to bind to
bind = "0.0.0.0:8000"

# The number of worker processes for handling requests
workers = 1

# The type of worker processes to spawn
worker_class = "sync"  # Alternatively, use "gevent" for async workers

# The maximum number of requests a worker will process before restarting
max_requests = 1000

# The maximum number of seconds a worker will live
max_request_jitter = 120

# Set the timeout for worker processes to gracefully finish
timeout = 30

# Logging configuration
accesslog = "/dcsp/logs/gunicorn/access.log"
errorlog = "/dcsp/logs/gunicorn/error.log"
loglevel = "info"

# Enable debugging mode (False in production)
debug = True

# Preload the application before the worker processes are forked
# preload_app = True

reload = True
reload_extra_files = find_html_files(c.TEMPLATES_FOLDER)

# The path to the application module or callable
# For example, "myapp:app" means "from myapp import app"
# or "myapp:create_app()" if create_app is a callable
# application that returns the WSGI app instance
wsgi_app = "dcsp.wsgi:application"
