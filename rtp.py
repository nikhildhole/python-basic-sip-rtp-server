import socket

def rtp_echo_server(server_ip, rtp_port, remote_sdp, stop_event):
    remote_ip = None
    remote_port = None

    for line in remote_sdp.splitlines():
        if line.startswith("c=IN IP4"):
            remote_ip = line.split()[-1]
        elif line.startswith("m=audio"):
            remote_port = int(line.split()[1])

    if not remote_ip or not remote_port:
        print("Invalid SDP, RTP not started")
        return

    print(f"RTP echo listening on {server_ip}:{rtp_port}")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((server_ip, rtp_port))
    sock.settimeout(1)

    while not stop_event.is_set():
        try:
            data, addr = sock.recvfrom(2048)
        except socket.timeout:
            continue

        # Echo RTP packet back to sender
        sock.sendto(data, addr)

    sock.close()
    print(f"RTP stopped on port {rtp_port}")
