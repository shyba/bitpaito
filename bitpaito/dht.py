import asyncio
import logging
from ipaddress import IPv4Address

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level='INFO')
log = logging.getLogger(__name__)
from asyncio import DatagramProtocol, DatagramTransport
from typing import Any

from bitpaito import bencode
from bitpaito.constants import PEER_ID


def from_compact_ip4(compact: bytes):
    assert len(compact) == 6, "Invalid compact"
    return IPv4Address(int.from_bytes(compact[:4], 'big')), int.from_bytes(compact[-2:], 'big')


class DHTProtocol(DatagramProtocol):
    def __init__(self):
        self.transport: DatagramTransport = None

    def connection_made(self, transport):
        log.info("Connected.")
        self.transport = transport

    def datagram_received(self, data: bytes, addr: tuple[str | Any, int]) -> None:
        log.info("RECV %s from %s", data, addr)
        data = bencode.decode(data)
        log.info("DECODE %s", data)
        log.info("IP: %s", from_compact_ip4(data[b"ip"]))

    def error_received(self, exc: Exception) -> None:
        log.error("ERR %s", exc)

    def connection_lost(self, exc: Exception | None) -> None:
        log.error("LOST")
        self.transport = None

    def sendto(self, data: bytes, addr: tuple[str | Any, int]) -> None:
        log.info("SEND %s %s", data, addr)
        self.transport.sendto(data, addr)


if __name__ == '__main__':
    async def test():
        loop = asyncio.get_event_loop()
        transport, proto = await loop.create_datagram_endpoint(DHTProtocol, local_addr=('0.0.0.0', 0))
        log.info('created')
        proto.sendto(bencode.encode(
            {"t": "bp", "y": "q", "q": "ping", "a": {"id": PEER_ID}}), ("67.215.246.10", 6881))
        try:
            await asyncio.sleep(1000)
        finally:
            transport.close()
    asyncio.run(test())
