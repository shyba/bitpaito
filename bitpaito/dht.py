import asyncio
import logging
import random
from collections import namedtuple
from ipaddress import IPv4Address
from itertools import cycle

log = logging.getLogger(__name__)
from asyncio import DatagramProtocol, DatagramTransport
from typing import Any, Callable, List, Optional

from bitpaito import bencode
from bitpaito.constants import SHORT_PEER_ID, DHT_DEFAULT_TIMEOUT


def from_compact_ip4(compact: bytes):
    assert len(compact) == 6, "Invalid compact"
    return IPv4Address(int.from_bytes(compact[:4], 'big')), int.from_bytes(compact[-2:], 'big')


def to_compact_ip4(ip: str | bytes, port):
    ip = ip.decode() if isinstance(ip, bytes) else ip
    return IPv4Address(ip).packed + int.to_bytes(port, 2, 'big')


RPCPeer = namedtuple('RPCPeer', "ip port node_id")


class DHT:
    def __init__(self, network: 'DHTNetwork'):
        self.network = network

    def ping(self, peer: RPCPeer):
        return self.network.query(peer, 'ping')


class DHTNetwork:
    def __init__(self, protocol: 'DHTProtocol'):
        self.protocol = protocol
        self.node_id = None
        self.port = protocol.port
        self.protocol.add_listener(self.handle_packet)
        self.pending = {}
        self._tgen = cycle(range(255))
        self.timeout = DHT_DEFAULT_TIMEOUT
        self.peers = {}

    @property
    def query_id(self) -> bytes:
        return bytes([next(self._tgen)])

    def reply(self, query_name: bytes, params=None):
        if query_name == b'ping':
            return {}

    def handle_packet(self, data: bytes, addr: tuple[str | Any, int]) -> None:
        data = bencode.decode(data)
        log.debug("[DECODED] %s FROM %s", data, addr)
        if b'y' not in data or b't' not in data:
            return log.debug("DROP BAD DATA FROM %s", addr)
        if data.get(b'ip'):
            data[b'ip'] = from_compact_ip4(data[b'ip'])
            log.debug("%s TOLD WE ARE %s", addr, data[b"ip"])
        if data[b'y'] in (b'r', b'e'):
            cb = self.pending.get((data[b't'], addr[0], addr[1]))
            if not cb:
                return log.debug("DROP UNSOLICITED RESPONSE FROM %s", addr)
            elif cb.done():
                return log.debug("DROP REPEATED RESPONSE FROM %s", addr)
            else:
                if data[b'y'] == b'r':
                    cb.set_result(data[b'r'])
                else:
                    cb.set_exception(Exception(data.get(b'e', data)))
        elif data[b'y'] == b'q':
            if b'q' not in data:
                return log.debug("QUERY WITHOUT NAME FROM %s", addr)
            log.debug("QUERY FROM %s", addr)
            response = {
                b'ip': to_compact_ip4(*addr), b'y': b'r',
                b'r': self.reply(data[b'q'], data[b'a']),
                b't': data.get(b't', b'\x00')
            }
            response[b'r'][b'id'] = self.node_id or random.randbytes(20)
            self.protocol.sendto(bencode.encode(response), addr)
        else:
            return log.debug("DROP INVALID y (%s) from %s", data[b'y'], addr)

    def cancel_or_remove(self, query_id: bytes, peer: RPCPeer):
        if cb := self.pending.pop((query_id, peer.ip, peer.port), None):
            if not cb.done():
                cb.set_exception(TimeoutError())

    async def query(self, peer: RPCPeer, query_name: str | bytes, **kwargs):
        kwargs["id"] = self.node_id or random.randbytes(20)
        kwargs = {"t": self.query_id, "v": SHORT_PEER_ID, "y": "q", "q": query_name, "a": kwargs}
        self.protocol.sendto(bencode.encode(kwargs), (peer.ip, peer.port))
        cb = asyncio.get_event_loop().create_future()
        self.pending[(kwargs["t"], peer.ip, peer.port)] = cb
        cb.add_done_callback(lambda _: self.cancel_or_remove(kwargs["t"], peer))
        return await asyncio.wait_for(cb, timeout=self.timeout)


class DHTProtocol(DatagramProtocol):
    def __init__(self):
        self.transport: Optional[DatagramTransport] = None
        self.port = None
        self.handlers: List[Callable[[bytes, tuple[str | Any, int]], None]] = []

    def add_listener(self, listener: Callable[[bytes, tuple[str | Any, int]], None]):
        self.handlers.append(listener)

    def connection_made(self, transport):
        log.debug("Connected.")
        self.transport = transport
        self.port = self.transport._sock.getsockname()[1]

    def datagram_received(self, data: bytes, addr: tuple[str | Any, int]) -> None:
        log.debug("RECV %s from %s", data, addr)
        for handler in self.handlers:
            asyncio.get_event_loop().call_soon(handler, data, addr)

    def error_received(self, exc: Exception) -> None:
        log.error("ERR %s", exc)

    def connection_lost(self, exc: Exception | None) -> None:
        log.error("CONNECTION LOST")
        self.transport = None

    def sendto(self, data: bytes, addr: tuple[str | Any, int]) -> None:
        log.debug("SEND %s %s", data, addr)
        self.transport.sendto(data, addr)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level='DEBUG')
    async def test():
        loop = asyncio.get_event_loop()
        transport, proto = await loop.create_datagram_endpoint(DHTProtocol, local_addr=('0.0.0.0', 0))
        log.debug('created')
        dht = DHT(DHTNetwork(proto))
        await dht.ping(RPCPeer("67.215.246.10", 6881, None))
        transport.close()
    asyncio.run(test())
