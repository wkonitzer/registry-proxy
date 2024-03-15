# Container Proxy Server for Mirantis Software Releases

This project features a Flask-based proxy server designed specifically for streamlining software retrieval from mirantis repositories. It serves as an efficient solution for environments where firewall restrictions limit outbound connections to a single whitelisted URL. Typically, fetching images from Mirantis involves accessing various data URLs, most commonly those under \*.blob.core.windows.net, which can be problematic in tightly secured networks. By routing all requests through this proxy, users can adhere to strict firewall rules while still accessing necessary container images, as all data appears to come directly from the whitelisted mirantis.azurecr.io domain, effectively bypassing the direct need for multiple whitelist entries such as those associated with Azure Blob Storage.

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