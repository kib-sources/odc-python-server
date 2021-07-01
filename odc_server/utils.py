def is_hex_24(a: str) -> bool:
    if len(a) != 24:
        return False
    try:
        int(a, 16)
    except:
        return False
    return True
