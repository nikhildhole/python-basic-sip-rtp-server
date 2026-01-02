import unittest
from sip_message import SIPMessage

class TestSIPMessage(unittest.TestCase):
    def test_parse_register(self):
        raw = (
            "REGISTER sip:example.com SIP/2.0\r\n"
            "Via: SIP/2.0/UDP 10.0.0.1:5060;branch=z9hG4bK-1234\r\n"
            "From: <sip:alice@example.com>;tag=1\r\n"
            "To: <sip:alice@example.com>\r\n"
            "Call-ID: 123456789\r\n"
            "CSeq: 1 REGISTER\r\n"
            "Content-Length: 0\r\n"
            "\r\n"
        )
        msg = SIPMessage(raw)
        self.assertTrue(msg.valid)
        self.assertTrue(msg.is_request())
        self.assertEqual(msg.method(), "REGISTER")
        self.assertEqual(msg.header("call-id"), "123456789")

    def test_parse_invalid(self):
        msg = SIPMessage("INVALID DATA")
        self.assertFalse(msg.valid)

if __name__ == "__main__":
    unittest.main()
