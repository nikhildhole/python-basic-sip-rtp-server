class SIPResponse:
    def __init__(self, code, reason, req):
        self.code = code
        self.reason = reason
        self.req = req
        self.headers = {}
        self.body = ""
        self._build_headers()

    def _build_headers(self):
        for h in ["via", "from", "call-id", "cseq"]:
            if self.req.header(h):
                self.headers[h] = self.req.header(h)

        to = self.req.header("to")
        if to and "tag=" not in to:
            to += ";tag=echo123"
        self.headers["to"] = to
        self.headers["content-length"] = "0"

    def build(self):
        lines = [f"SIP/2.0 {self.code} {self.reason}"]
        for k, v in self.headers.items():
            lines.append(f"{k.title()}: {v}")
        lines.append("")
        lines.append(self.body)
        return "\r\n".join(lines)
