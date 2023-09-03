SHORT_PEER_ID = b'BP01'
PEER_ID = b'-' + SHORT_PEER_ID + b'---------------'
assert len(PEER_ID) == 20, len(PEER_ID)
MAGIC = b'\x13BitTorrent protocol'
DHT_DEFAULT_TIMEOUT = 10
