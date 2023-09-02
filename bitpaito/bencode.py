def encode(what: str | bytes | int | list):
    if isinstance(what, str):
        what = what.encode()
    if isinstance(what, bytes):
        return str(len(what)).encode() + b':' + what
    if isinstance(what, int):
        return b'i'+str(what).encode()+b'e'
    if isinstance(what, list):
        return b'l'+b''.join(encode(i) for i in what)+b'e'


def decode(what: bytes):
    state = START
    size = 0
    ret = None
    neg = False
    for c in what:
        if state in (START, WANT_COLON):
            if c == ord(b'i'):
                state = WANT_INTEGER
            elif ord(b'0') <= c <= ord(b'9'):
                state = WANT_COLON
                size = size*10 + int(chr(c))
            elif c == ord(b':'):
                if state == WANT_COLON:
                    state = WANT_ATOMS
                    ret = []
                else:
                    raise ValueError(f'Got a : in state {state}')
            else:
                raise ValueError(f'Unknown state {state} with token {chr(c)}')
        elif state == WANT_ATOMS and size > 0:
            ret.append(c)
            size -= 1
            if size == 0:
                return bytes(ret).decode()
        elif state == WANT_INTEGER:
            if c == ord(b'-') and size == 0:
                neg = True
            elif ord(b'0') <= c <= ord(b'9'):
                size = size*10 + int(chr(c))
            elif c == ord(b'e'):
                return size if not neg else -size
            else:
                raise ValueError(f'Got {chr(c)}({c}) expecting integer or e.')
        else:
            raise ValueError(f'Unknown state {state} with token {chr(c)}')
    raise ValueError(f'Unexpected end at {state}')



START = 1
WANT_COLON = 2
WANT_ATOMS = 3
WANT_INTEGER = 4
