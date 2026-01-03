class SIPMessage:
    def __init__(self, raw: str):
        self.raw = raw.strip()
        self.start_line = ""
        self.headers = {}
        self.body = ""
        self.valid = False

        if self.raw:
            self._parse()

    def _parse(self):
        parts = self.raw.split("\r\n\r\n", 1)
        header_part = parts[0]
        self.body = parts[1] if len(parts) == 2 else ""

        lines = header_part.split("\r\n")
        if not lines or not lines[0]:
            return

        self.start_line = lines[0]
        if "SIP/2.0" not in self.start_line:
            return

        self.valid = True

        for line in lines[1:]:
            if ":" in line:
                name, value = line.split(":", 1)
                self.headers[name.strip().lower()] = value.strip()

    def is_request(self):
        return self.valid and not self.start_line.startswith("SIP/2.0")

    def is_response(self):
        return self.valid and self.start_line.startswith("SIP/2.0")

    def method(self):
        if not self.valid:
            return None

        parts = self.start_line.split()
        if len(parts) < 1:
            return None

        return parts[0]

    def header(self, name):
        return self.headers.get(name.lower())
