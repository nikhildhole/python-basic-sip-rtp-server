import socket
import threading
from sip_message import SIPMessage
from sip_response import SIPResponse
from rtp import rtp_echo_server

SERVER_IP = "127.0.0.1"   # CHANGE to LAN IP if needed
SIP_PORT = 5060
RTP_PORT = 40000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((SERVER_IP, SIP_PORT))

print("SIP Echo Server running on UDP 5060")

call_state = {
    "rtp_stop": None
}

def send(msg, addr):
    sock.sendto(msg.encode(), addr)

def build_sdp(ip, rtp_port):
    return (
        "v=0\r\n"
        "o=echo 1234 1234 IN IP4 {ip}\r\n"
        "s=Echo\r\n"
        "c=IN IP4 {ip}\r\n"
        "t=0 0\r\n"
        "m=audio {port} RTP/AVP 8\r\n"
        "a=rtpmap:8 PCMA/8000\r\n"
    ).format(ip=ip, port=rtp_port)

while True:
    data, addr = sock.recvfrom(65535)
    raw = data.decode(errors="ignore")

    print("\n--- SIP MESSAGE ---\n", raw)

    msg = SIPMessage(raw)

    if not msg.valid:
        print("Ignored empty/invalid SIP packet")
        continue


    # REGISTER not supported
    if msg.is_request() and msg.method() == "REGISTER":
        resp = SIPResponse(405, "Method Not Allowed", msg)
        resp.headers["allow"] = "INVITE, ACK, BYE, OPTIONS"
        send(resp.build(), addr)

    # OPTIONS health check
    elif msg.is_request() and msg.method() == "OPTIONS":
        send(SIPResponse(200, "OK", msg).build(), addr)

    elif msg.is_request() and msg.method() == "INVITE":
        # Initial INVITE or re-INVITE
        send(SIPResponse(100, "Trying", msg).build(), addr)

        # If re-INVITE has SDP, accept it
        if msg.body:
            sdp = build_sdp(SERVER_IP, RTP_PORT)
        else:
            sdp = ""

        resp = SIPResponse(200, "OK", msg)
        resp.headers["contact"] = f"<sip:echo@{SERVER_IP}:{SIP_PORT}>"

        if sdp:
            resp.headers["content-type"] = "application/sdp"
            resp.headers["content-length"] = str(len(sdp))
            resp.body = sdp

        send(resp.build(), addr)

        # Start RTP only on first INVITE
        if not call_state.get("rtp_stop"):
            stop_event = threading.Event()
            call_state["rtp_stop"] = stop_event

            threading.Thread(
                target=rtp_echo_server,
                args=(SERVER_IP, RTP_PORT, msg.body, stop_event),
                daemon=True
            ).start()

    # INVITE
    elif msg.is_request() and msg.method() == "INVITE":
        send(SIPResponse(100, "Trying", msg).build(), addr)

        sdp = build_sdp(SERVER_IP, RTP_PORT)

        resp = SIPResponse(200, "OK", msg)
        resp.headers["contact"] = f"<sip:echo@{SERVER_IP}:{SIP_PORT}>"
        resp.headers["content-type"] = "application/sdp"
        resp.headers["content-length"] = str(len(sdp))
        resp.body = sdp

        send(resp.build(), addr)

        stop_event = threading.Event()
        call_state["rtp_stop"] = stop_event

        threading.Thread(
            target=rtp_echo_server,
            args=(SERVER_IP, RTP_PORT, msg.body, stop_event),
            daemon=True
        ).start()

    # BYE
    elif msg.is_request() and msg.method() == "BYE":
        if call_state["rtp_stop"]:
            call_state["rtp_stop"].set()

        send(SIPResponse(200, "OK", msg).build(), addr)
