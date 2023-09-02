from unittest import TestCase

from bitpaito import bencode


class TestBencode(TestCase):
    def test_encode(self):
        # bit strings
        self.assertEqual(b'9:something', bencode.encode('something'))
        self.assertEqual(b'14:something else', bencode.encode('something else'))
        self.assertEqual(b'4:'+'😱'.encode(), bencode.encode('😱'))
        # integers
        self.assertEqual(b'i42e', bencode.encode(42))
        self.assertEqual(b'i-42e', bencode.encode(-42))
        self.assertEqual(b'i40000000000e', bencode.encode(40_000_000_000))
        self.assertEqual(b'i40000000000e', bencode.encode(40_000_000_000))
        # list
        self.assertEqual(b'l3:foei2ee', bencode.encode(["foe", 2]))
        self.assertEqual(b'li1ei2ei3ee', bencode.encode([1, 2, 3]))
        self.assertEqual(b'l1:ee', bencode.encode(["e"]))
        self.assertEqual(b'le', bencode.encode([]))

    def test_decode(self):
        # bit strings
        self.assertEqual('something', bencode.decode(b'9:something'))
        self.assertEqual('batata frita', bencode.decode(b'12:batata frita'))
        self.assertEqual('😱', bencode.decode('4:😱'.encode()))
        # integers
        self.assertEqual(42, bencode.decode(b'i42e'))
        self.assertEqual(-42, bencode.decode(b'i-42e'))
        self.assertEqual(40_000_000_000, bencode.decode(b'i40000000000e'))
        # lists
        self.assertEqual(["foe", 2], bencode.decode(b'l3:foei2ee'))
        self.assertEqual([1, 2, 3], bencode.decode(b'li1ei2ei3ee'))
        self.assertEqual(["e"], bencode.decode(b'l1:ee'))
        self.assertEqual([], bencode.decode(b'le'))
