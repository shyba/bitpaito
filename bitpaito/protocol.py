from dataclasses import dataclass
from typing import Optional
from .constants import PEER_ID, MAGIC


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


@dataclass
class RawMessage:
    payload: bytes

    @property
    def length(self):
        return self.payload[0]

    @property
    def id(self):
        return None if self.length == 0 else self.payload[4]

    @property
    def valid(self):
        if self.length == 0:
            return len(self.payload) == 4
        return len(self.payload) == self.length + 4

    @classmethod
    def eat(cls, stream: bytes):
        if len(stream) < 4:
            return None, stream
        length = int.from_bytes(stream[0:4], 'big')
        if len(stream) < 4 + length:
            return None, stream
        return cls(stream[:(4+length)]), stream[(4+length):]


class TorrentProtocolStateMachine:
    WANT_HANDSHAKE = 1
    CONNECTED = 2
    ERROR = 0xff

    def __init__(self):
        self.handshake: Optional[HandshakeMessage] = None
        self._state = self.WANT_HANDSHAKE
        self._trailing = b''
        self.messages = []

    @property
    def valid(self):
        return self._state != self.ERROR

    def eat(self, stream: bytes):
        if not stream or self._state == self.ERROR:
            return
        self._trailing += stream
        if self._state == self.WANT_HANDSHAKE and len(self._trailing) >= 68:
            if self._trailing[0] != 0x13:
                return self._error()
            handshake = HandshakeMessage.decode(self._trailing[:68])
            self.handshake = handshake
            self._state = self.CONNECTED
            self._trailing = self._trailing[68:]
        if self._state == self.CONNECTED:
            msg, remaining = RawMessage.eat(self._trailing)
            while msg:
                if not msg.valid:
                    return self._error()
                self.messages.append(msg)
                msg, remaining = RawMessage.eat(remaining)
            self._trailing = remaining

    def _error(self):
        self._state = self.ERROR
        self._trailing = b''

