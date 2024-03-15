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

AZURE_REGISTRY_URL = 'https://mirantis.azurecr.io'  # Actual Azure registry URL

@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'HEAD'])
def proxy_request(path):
    """
    Acts as a proxy for requests to the Azure Container Registry.

    This function intercepts incoming HTTP requests, logs their details,
    and then forwards them to the specified Azure Container Registry URL.
    It modifies the incoming requests by ensuring the 'Host' header is
    appropriate for the Azure endpoint and by maintaining any 'Authorization'
    headers present.

    Args:
        path (str): The specific path in the Azure Container Registry that the
                    request is trying to access. This could include image names,
                    tags, or other registry-specific information.

    Returns:
        Response: A Flask Response object that streams the content from the
                  Azure registry response back to the client. This includes
                  status code, headers, and body of the response.
    """

    # Log incoming request details
    logging.info('Incoming request: %s %s', request.method, request.full_path)
    logging.debug('Request headers: %s', {request.headers})
    if 'Authorization' in request.headers:
        logging.debug('Incoming Authorization header: %s',
                        request.headers["Authorization"])

    # Construct the URL based on the actual request
    real_url = f"{AZURE_REGISTRY_URL}/{path}"
    if request.query_string:
        real_url += f'?{request.query_string.decode("utf-8")}'

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
