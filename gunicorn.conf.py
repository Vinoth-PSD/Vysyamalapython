# gunicorn.conf.py

# Number of worker processes
workers = 4

# Bind to port 8000
bind = "0.0.0.0:8000"

# Timeout for requests (in seconds)
timeout = 120

# Log level (debug, info, warning, error, critical)
loglevel = "info"

# Log file (optional)
# accesslog = "/path/to/access.log"
# errorlog = "/path/to/error.log"

# Preload the application
preload_app = True

# Maximum number of requests a worker will process before restarting
max_requests = 1000
max_requests_jitter = 50