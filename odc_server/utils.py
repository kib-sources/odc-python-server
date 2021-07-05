import random
import string


def is_hex(a: str, l: int) -> bool:
    if len(a) != l:
        return False
    try:
        int(a, 16)
    except:
        return False
    return True


def random_numerical_string(l):
    return ''.join(random.SystemRandom().choice(string.digits) for _ in range(l))
