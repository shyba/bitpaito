import asyncio
import logging
from unittest import IsolatedAsyncioTestCase

from bitpaito.dht import DHTProtocol, DHT, DHTNetwork, RPCPeer


class TestDHT(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level='DEBUG')
        self.node = await self.addNode()

    async def addNode(self):
        loop = asyncio.get_event_loop()
        transport, proto = await loop.create_datagram_endpoint(DHTProtocol, local_addr=('127.0.0.1', 0))
        dht = DHT(DHTNetwork(proto))
        self.addCleanup(transport.close)
        return dht

    async def test_ping(self):
        other = await self.addNode()
        await self.node.ping(RPCPeer('127.0.0.1', other.network.port, None))
