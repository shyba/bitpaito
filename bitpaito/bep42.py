import ipaddress

from bitpaito.crc32c import crc32c


def to_bep42(ip, node_id):
    rand = node_id[-1]
    ip = ipaddress.ip_address(ip).packed

    # ipint = int.from_bytes(ip, 'big')
    # print(hex(crc32c(((ipint & 0x030f3fff) | (rand << 29)).to_bytes(4, 'big'))))

    v4_mask = [ 0x03, 0x0f, 0x3f, 0xff ]
    v6_mask = [ 0x01, 0x03, 0x07, 0x0f, 0x1f, 0x3f, 0x7f, 0xff ]
    mask = v4_mask if len(ip) == 4 else v6_mask

    ip = list(c & mask[i] for i, c in enumerate(ip))

    rand = rand & 0xff
    r = rand & 0x7
    ip[0] |= r << 5

    crc = crc32c(ip)

    # only take the top 21 bits from crc
    node_id = list(node_id)
    node_id[0] = (crc >> 24) & 0xff
    node_id[1] = (crc >> 16) & 0xff
    node_id[2] = ((crc >> 8) & 0xf8) | (node_id[2] & 0x7)
    node_id[19] = rand
    return bytes(node_id)


def check(ip, node_id):
    return node_id == to_bep42(ip, node_id)
