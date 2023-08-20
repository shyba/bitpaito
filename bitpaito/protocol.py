from dataclasses import dataclass
from typing import Optional
PEER_ID = b'TEST-CLIENT---------'
MAGIC = b'\x13BitTorrent protocol'


@dataclass
class HandshakeMessage:
    reserved: bytes
    peer_id: bytes
    infohash: bytes

    def __init__(self, infohash: bytes, peer_id=None, reserved=None):
        self.reserved = reserved or (0).to_bytes(8, 'big')
        self.infohash = infohash
        self.peer_id = peer_id or PEER_ID

    def encode(self) -> bytes:
        if not self.validate():
            raise Exception(f'Trying to encode an invalid handhake {self}')
        return MAGIC + self.reserved + self.infohash + self.peer_id

    @classmethod
    def decode(cls, payload: bytes):
        assert payload and len(payload) == 68
        peer_id = payload[-20:]
        infohash = payload[-40:-20]
        msg = cls(infohash, peer_id)
        return msg if msg.validate() else None

    def validate(self) -> bool:
        return self.infohash and self.peer_id and len(self.infohash) == len(self.peer_id) == 20


def handshake(infohash: bytes, peer_id: Optional[bytes] = None) -> bytes:
    peer_id = peer_id or (0).to_bytes(20, 'big')
    reserved = (0).to_bytes(8, 'big')
    assert peer_id and infohash and len(peer_id) == len(infohash) == 20
    return b"\x13BitTorrent protocol" + reserved + infohash + peer_id
