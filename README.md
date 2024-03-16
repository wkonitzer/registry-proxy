# Unified Proxy Server for Mirantis Software Releases

This project introduces a Flask-based proxy server designed to facilitate container image and software package retrieval from various repositories, primarily focusing on Mirantis and Ubuntu archives. It addresses the common challenge faced by environments with stringent firewall restrictions that only permit outbound connections to a predefined set of whitelisted URLs.

Traditionally, accessing container images from Mirantis or package updates from Ubuntu repositories requires connections to multiple data URLs, including those under \*.blob.core.windows.net and archive.ubuntu.com, posing a challenge in secure network environments. This proxy server routes all requests through a single, whitelisted domain, enabling users to comply with strict firewall policies while maintaining access to necessary resources.

The server acts as an intermediary, handling requests for Mirantis Docker images, Ubuntu package updates, and other software repositories by dynamically resolving and forwarding requests based on the 'Host' header. This approach allows all data to appear as if it is being served directly from the whitelisted domains, such as mirantis.azurecr.io or archive.ubuntu.com, thus eliminating the need for multiple whitelist entries and simplifying network security configurations.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Installation

Make sure you have python3 installed as a pre-requisite on a server running Ubuntu 22.04.

Clone the repository:
```shell
git clone https://github.com/wkonitzer/registry-proxy.git
cd registry-proxy
```

Set up a virtual environment and activate it:

```shell
python -m venv venv
# For Windows
.\venv\Scripts\activate
# For Unix or MacOS
source venv/bin/activate
```

Install the required Python packages:
```shell
pip install -r requirements.txt
```

## Usage

Start the TLS proxy:

```shell
gunicorn --certfile mirantis.azurecr.io.crt --keyfile mirantis.azurecr.io.key --log-level info -w 1 -b 0.0.0.0:443 container_proxy:app &
```

Start the http proxy:
```shell
gunicorn --log-level info -w 1 -b 0.0.0.0:80 container_proxy:app &
```

Configure client server:

1. Copy the `myCA.crt` file to `/usr/local/share/ca-certificates/`
2. Update the CA certificates:
    ```shell
    sudo update-ca-certificates
    ```
3. Restart Docker to apply the new CA certificates:
    ```shell
    systemctl restart docker
    ```
4. Add the proxy server's IP address to your `/etc/hosts` file so your machine can recognize the custom domain name. Open the hosts file:
    ```shell
    sudo vi /etc/hosts
    ```
   Then add a line with the proxy server's IP address followed by `mirantis.azurecr.io`. For example:
    ```text
    192.168.1.100 mirantis.azurecr.io
    ```

Test:

On client machine run `docker pull mirantis.azurecr.io/general/mariadb:10.4.16-bionic-20201105025052`
Verify the image pulls and server show logs.

## Contributing

Contributions are welcome! If you'd like to contribute to this project, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and test them.
4. Commit your changes with clear and concise messages.
5. Push your changes to your fork.
6. Create a pull request to the main repository.

## License

This project is licensed under the MIT License.