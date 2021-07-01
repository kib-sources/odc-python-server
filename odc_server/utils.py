import random
import string


def is_hex_24(a: str) -> bool:
    if len(a) != 24:
        return False
    try:
        int(a, 16)
    except:
        return False
    return True


def random_numerical_string(l):
    return ''.join(random.SystemRandom().choice(string.digits) for _ in range(l))
