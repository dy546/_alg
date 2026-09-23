
def t1(n):
    """T(n) = T(n-1) + 8, T(1) = 1.  Closed form: 8n - 7, O(n)."""
    if n == 1:
        return 1
    return t1(n - 1) + 8


def t2(n):
    """T(n) = 2*T(n-1) + 9, T(1) = 1.  Closed form: 10*2^(n-1) - 9, O(2^n)."""
    if n == 1:
        return 1
    return 2 * t2(n - 1) + 9


def t3(n):
    """T(n) = 2*T(n/2) + 1, T(1) = 1.  Closed form: 2n - 1, O(n).

    n must be a power of 2.
    """
    if n == 1:
        return 1
    return 2 * t3(n // 2) + 1


def t4(n):
    """T(n) = T(n/2) + 1, T(1) = 1.  Closed form: log2(n) + 1, O(log n).

    n must be a power of 2.
    """
    if n == 1:
        return 1
    return t4(n // 2) + 1


def t1_closed(n):
    return 8 * n - 7


def t2_closed(n):
    return 10 * 2 ** (n - 1) - 9


def t3_closed(n):
    return 2 * n - 1


def t4_closed(n):
    return n.bit_length()  # floor(log2(n)) + 1, exact for powers of 2


def is_power_of_two(n):
    return n > 0 and (n & (n - 1)) == 0
