from unittest import TestCase

from bitpaito import bencode


class TestBencode(TestCase):
    def test_encode(self):
        self.assertEqual(b'9:something', bencode.encode('something'))
        self.assertEqual(b'14:something else', bencode.encode('something else'))
        self.assertEqual(b'4:'+'😱'.encode(), bencode.encode('😱'))
        self.assertEqual(b'i42e', bencode.encode(42))
        self.assertEqual(b'i-42e', bencode.encode(-42))
        self.assertEqual(b'i40000000000e', bencode.encode(40_000_000_000))

    def test_decode(self):
        self.assertEqual('something', bencode.decode(b'9:something'))
        self.assertEqual('batata frita', bencode.decode(b'12:batata frita'))
        self.assertEqual('😱', bencode.decode('4:😱'.encode()))
        self.assertEqual(42, bencode.decode(b'i42e'))
        self.assertEqual(-42, bencode.decode(b'i-42e'))
        self.assertEqual(40_000_000_000, bencode.decode(b'i40000000000e'))
