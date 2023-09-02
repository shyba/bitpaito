def encode(what: str | bytes):
    if isinstance(what, str):
        what = what.encode()
    if isinstance(what, bytes):
        return str(len(what)).encode() + b':' + what
