import socket
import threading
from sip_message import SIPMessage
from sip_response import SIPResponse
from rtp import rtp_echo_server
from sip_utils import get_called_number, get_caller_number  

SERVER_IP = "127.0.0.1"   # change to LAN IP if needed
SIP_PORT = 5060

RTP_PORT_START = 40000
RTP_PORT_END = 41000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((SERVER_IP, SIP_PORT))

print("SIP Echo Server running on UDP 5060")

# call-id -> call data
calls = {}
used_ports = set()


def send(msg, addr):
    sock.sendto(msg.encode(), addr)


def allocate_rtp_port():
    for port in range(RTP_PORT_START, RTP_PORT_END, 2):
        if port not in used_ports:
            used_ports.add(port)
            return port
    raise RuntimeError("No RTP ports available")


def release_rtp_port(port):
    used_ports.discard(port)


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
        continue

    # -------- REGISTER --------
    if msg.is_request() and msg.method() == "REGISTER":
        resp = SIPResponse(405, "Method Not Allowed", msg)
        resp.headers["allow"] = "INVITE, ACK, BYE, OPTIONS, UPDATE"
        send(resp.build(), addr)

    # -------- OPTIONS --------
    elif msg.is_request() and msg.method() == "OPTIONS":
        send(SIPResponse(200, "OK", msg).build(), addr)

    # -------- UPDATE --------
    elif msg.is_request() and msg.method() == "UPDATE":
        send(SIPResponse(200, "OK", msg).build(), addr)

    # -------- INVITE (new or re-INVITE) --------
    elif msg.is_request() and msg.method() == "INVITE":
        called = get_called_number(msg)
        caller = get_caller_number(msg)

        print("📞 Incoming Call")
        print("  DID   :", called)
        print("  Caller:", caller)
    
        call_id = msg.header("call-id")
        if not call_id:
            continue

        send(SIPResponse(100, "Trying", msg).build(), addr)

        # re-INVITE
        if call_id in calls:
            send(SIPResponse(200, "OK", msg).build(), addr)
            continue

        # new call
        rtp_port = allocate_rtp_port()
        sdp = build_sdp(SERVER_IP, rtp_port)

        resp = SIPResponse(200, "OK", msg)
        resp.headers["contact"] = f"<sip:echo@{SERVER_IP}:{SIP_PORT}>"
        resp.headers["content-type"] = "application/sdp"
        resp.headers["content-length"] = str(len(sdp))
        resp.body = sdp

        send(resp.build(), addr)

        stop_event = threading.Event()

        thread = threading.Thread(
            target=rtp_echo_server,
            args=(SERVER_IP, rtp_port, msg.body, stop_event),
            daemon=True
        )
        thread.start()

        calls[call_id] = {
            "rtp_port": rtp_port,
            "rtp_stop": stop_event,
            "thread": thread
        }

        print(f"Call started {call_id} RTP={rtp_port}")

    # -------- BYE --------
    elif msg.is_request() and msg.method() == "BYE":
        call_id = msg.header("call-id")

        if call_id in calls:
            calls[call_id]["rtp_stop"].set()
            release_rtp_port(calls[call_id]["rtp_port"])
            del calls[call_id]
            print(f"Call ended {call_id}")

        send(SIPResponse(200, "OK", msg).build(), addr)
