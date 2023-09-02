from unittest import TestCase

from bitpaito import bencode


class TestBencode(TestCase):
    def test_encode(self):
        self.assertEqual(b'9:something', bencode.encode('something'))
        self.assertEqual(b'14:something', bencode.encode('something else'))

    def test_decode(self):
        self.assertEqual('something', bencode.decode(b'9:something'))
        self.assertEqual('batata frita', bencode.decode(b'12:batata frita'))
