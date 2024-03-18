#!/bin/sh

# Check if running in HTTPS mode
if [ "$MODE" = "https" ]; then
    # Start Gunicorn with SSL configuration
    exec gunicorn --certfile server.crt \
                  --keyfile server.key \
                  -w 1 -b 0.0.0.0:8443 container_proxy:app
else
    # Start Gunicorn without SSL configuration
    exec gunicorn -w 1 -b 0.0.0.0:8080 container_proxy:app
fi
