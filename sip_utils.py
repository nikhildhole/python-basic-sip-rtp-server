import re

def extract_sip_number(value):
    """
    Extract number from sip:<number>@...
    """
    if not value:
        return None

    match = re.search(r"sip:([^@;>]+)", value)
    return match.group(1) if match else None


def get_called_number(msg):
    # 1) Request-URI
    if msg.is_request():
        parts = msg.start_line.split()
        if len(parts) >= 2 and parts[1].startswith("sip:"):
            num = extract_sip_number(parts[1])
            if num:
                return num

    # 2) P-Called-Party-ID
    num = extract_sip_number(msg.header("p-called-party-id"))
    if num:
        return num

    # 3) To
    num = extract_sip_number(msg.header("to"))
    if num:
        return num

    # 4) Diversion
    num = extract_sip_number(msg.header("diversion"))
    if num:
        return num

    return None


def get_caller_number(msg):
    # 1) P-Asserted-Identity
    num = extract_sip_number(msg.header("p-asserted-identity"))
    if num:
        return num

    # 2) From
    num = extract_sip_number(msg.header("from"))
    if num:
        return num

    return None
