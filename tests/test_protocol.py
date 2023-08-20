from unittest import TestCase

from bitpaito.protocol import HandshakeMessage


class TestHandshakeMessage(TestCase):
    def test_handshake_encode_decode_validate(self):
        h = HandshakeMessage(bytes([i for i in range(20)]))
        encoded = h.encode()
        self.assertEqual(68, len(encoded))
        self.assertEqual(0x13, encoded[0])
        self.assertEqual(b'BitTorrent protocol', encoded[1:0x13+1])
        self.assertEquals(h.peer_id, encoded[-20:])
        self.assertEquals(bytes([i for i in range(20)]), encoded[-40:-20])
        h2 = HandshakeMessage.decode(encoded)
        self.assertEqual(h, h2)
