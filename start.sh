#!/bin/sh

# Check if running in HTTPS mode
if [ "$MODE" = "https" ]; then
    # Start Gunicorn with SSL configuration
    exec gunicorn --certfile /etc/ssl/certs/server.crt \
                  --keyfile /etc/ssl/certs/server.key \
                  --log-level $LOGGING_LEVEL -w 1 -b 0.0.0.0:8443 container_proxy:app
else
    # Start Gunicorn without SSL configuration
    exec gunicorn --log-level $LOGGING_LEVEL -w 1 -b 0.0.0.0:8080 container_proxy:app
fi
