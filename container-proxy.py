import logging
from flask import Flask, request, Response
import requests

# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

AZURE_REGISTRY_URL = 'https://mirantis.azurecr.io'  # Actual Azure registry URL

@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'HEAD'])
def proxy_request(path):
    # Log incoming request details
    logging.info(f'Incoming request: {request.method} {request.full_path}')
    logging.debug(f'Request headers: {request.headers}')
    if 'Authorization' in request.headers:
        logging.debug(f'Incoming Authorization header: {request.headers["Authorization"]}')    

    # Construct the real URL based on the actual request
    real_url = f"{AZURE_REGISTRY_URL}/{path}"
    if request.query_string:
        real_url += f'?{request.query_string.decode("utf-8")}'

    # Forward the request to the actual Azure registry
    headers = {key: value for key, value in request.headers}
    headers.pop('Host', None)
    response = requests.request(method=request.method, url=real_url, headers=headers, stream=True)

    # Log outgoing request Authorization header
    if 'Authorization' in headers:
        logging.debug(f'Outgoing Authorization header: {headers["Authorization"]}')

    # Log response details
    logging.info(f'Response status: {response.status_code}')
    logging.debug(f'Response headers: {response.headers}')

    # Stream the response back to the client
    return Response(response.iter_content(chunk_size=1024), status=response.status_code, headers=dict(response.headers))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')  # WARNING: For local testing only; use a proper server for production

