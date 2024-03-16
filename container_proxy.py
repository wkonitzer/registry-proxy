"""
This Flask application acts as a proxy server for Docker image requests to the
Azure Container Registry. It intercepts incoming requests, logs request and
response details, and forwards the requests to the specified Azure registry URL
while stripping out inappropriate headers and appending necessary ones.

The application supports GET, POST, PUT, DELETE, and HEAD HTTP methods to
accommodate various types of registry interactions such as pulling images,
pushing images, and querying image information.

The app also handles the redirection of authorization headers to ensure secure
communication between the client and Azure services while maintaining the
integrity of the request-response cycle.
"""

import logging
from flask import Flask, request, Response
import requests

# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Define base URLs for different repositories
REPO_BASE_URLS = {
    'azure': 'https://mirantis.azurecr.io',
    'repos': 'https://repos.mirantis.com',
    'binary': 'https://binary.mirantis.com',
    'mirror': 'https://mirror.mirantis.com',
    'deb': 'https://deb.nodesource.com',
    'archive': 'http://archive.ubuntu.com',
    'security': 'http://security.ubuntu.com'
}

# Derive the mapping from 'Host' header to repo_type based on REPO_BASE_URLS
HOST_TO_REPO_TYPE = {
    url.replace('https://', '').replace('http://', ''): repo
    for repo, url in REPO_BASE_URLS.items()
}

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT',
                                                'DELETE', 'HEAD'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'HEAD'])
def proxy_request(path):
    """
    Acts as a proxy for requests based on the 'Host' header.

    The function intercepts incoming HTTP requests, identifies the intended
    repository based on the 'Host' header, and forwards the requests
    accordingly.
    """

    # Log incoming request details
    logging.info('Incoming request: %s %s', request.method, request.full_path)
    logging.debug('Request headers: %s', request.headers)
    if 'Authorization' in request.headers:
        logging.debug('Incoming Authorization header: %s',
                        request.headers["Authorization"])

    # Determine the repository type based on the 'Host' header
    host_header = request.headers.get('Host')
    repo_type = HOST_TO_REPO_TYPE.get(host_header)
    logging.debug('Host: %s', host_header)
    logging.info('Repo type: %s', repo_type)

    # Ensure the requested repository type is supported
    if not repo_type or repo_type not in REPO_BASE_URLS:
        return Response(f"Repository type for host {host_header} not supported",
                        status=400)

    # Construct the real URL based on the actual request
    base_url = REPO_BASE_URLS[repo_type]
    real_url = f"{base_url}/{path}"
    if request.query_string:
        real_url += f'?{request.query_string.decode("utf-8")}'

    logging.debug('Upstream url to request: %s', real_url)

    # Forward the request to the Azure registry
    headers = dict(request.headers)
    headers.pop('Host', None) # Remove host to ensure proper forwarding
    response = requests.request(method=request.method, url=real_url,
                                headers=headers, stream=True, timeout=(10, 30))

    # Log outgoing request Authorization header
    if 'Authorization' in headers:
        logging.debug('Outgoing Authorization header: %s',
                        headers["Authorization"])

    # Log response details
    logging.info('Response status: %s', response.status_code)
    logging.debug('Response headers: %s', response.headers)

    # Stream the response back to the client
    return Response(response.iter_content(chunk_size=1024),
                    status=response.status_code, headers=dict(response.headers))


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
