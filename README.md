# Python Basic SIP RTP Server

A lightweight, containerized SIP Echo Server written in Python. It handles SIP signaling and establishes RTP sessions to echo back audio streams. This project is useful for testing SIP clients, load balancers, and network configurations.

## Features

- **SIP Signaling**: Handles `INVITE`, `ACK`, `BYE`, `OPTIONS`, `UPDATE` methods.
- **RTP Echo**: Automatically allocates UDP ports for RTP (default range 30000-30010) and echoes received audio packets back to the sender.
- **Container Ready**: Includes a `Dockerfile` for easy building and deployment.
- **Configurable**: Uses environment variables for IP binding and SDP advertising.
- **CI/CD Integrated**: Includes GitHub Actions for automated testing, linting, and container publishing.

## Prerequisites

- Python 3.x (Standard library only)
- Docker (Optional)
- Kubernetes / Minikube (Optional)

## Local Development

### Running with Python

The server relies on standard Python libraries. To run it locally:

1. **Start the Server**:
   ```bash
   # Default runs on 0.0.0.0:5060 and advertises 127.0.0.1 in SDP
   python server.py
   ```

2. **Custom Configuration**:
   You can override the bind IP and the advertised IP (used in the SDP body) using environment variables.

   ```bash
   # Example: Advertise your LAN IP to allow external softphones to connect
   export ADVERTISED_IP=192.168.1.50
   python server.py
   ```

### Running with Docker

1. **Build the Image**:
   ```bash
   docker build -t sip-echo .
   ```

2. **Run the Container**:
   You need to expose the SIP port (UDP 5060) and the RTP port range (UDP 30000-30010).

   ```bash
   docker run -d \
     -p 5060:5060/udp \
     -p 30000-30010:30000-30010/udp \
     -e ADVERTISED_IP=<YOUR_HOST_IP> \
     --name sip-echo \
     sip-echo
   ```

## Protocol Support

- **INVITE**: Initiates a session. The server replies with `200 OK` and an SDP body indicating where to send RTP audio.
- **BYE**: Ends the session and releases the allocated RTP port.
- **OPTIONS / UPDATE**: Responded with `200 OK`.
- **REGISTER**: Responded with `405 Method Not Allowed`.

## Deployment

### Kubernetes (Minikube)

To deploy this server on a local Minikube cluster:

1. **Start Minikube**:
   ```bash
   minikube start
   ```

2. **Deploy**:
   Ensure you have a valid `deploy.yaml` (Kubernetes manifest) defining your Deployment and Service.
   ```bash
   kubectl apply -f deploy.yaml
   ```

3. **Access**:
   Use `minikube tunnel` or `NodePort` depending on your service configuration to access the SIP server.

## Continuous Integration

This project uses **GitHub Actions** for:
- **Linting & CodeQL**: Ensures code quality and security.
- **Testing**: automated test execution.
- **Building Artifacts**: Builds multi-architecture Docker images.
- **Releasing**: Automates version bumping and Git tagging.

See [.github/workflows/ci.yaml](.github/workflows/ci.yaml) for the full workflow definition.
