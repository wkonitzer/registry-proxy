FROM python:3.11-slim-bookworm

# Set work directory
WORKDIR /app

# Update, upgrade system packages, and clean up in a single layer
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the requirements file
COPY requirements.txt .

# Upgrade pip and install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy your application code and SSL files
COPY start.sh container_proxy.py server.crt server.key ./

# Make sure the script and SSL files are readable/executable
RUN chmod +x start.sh && \
    chmod 644 server.crt server.key

# Make ports 8080 and 8443 available to the world outside this container
EXPOSE 8080 8443

# Create a non-root user and switch to it
RUN useradd -m --uid 1001 myuser
USER 1001

# Use the startup script as the container’s entrypoint
ENTRYPOINT ["./start.sh"]


