# 方法 1：直接用指數運算
def power2n(n):
    return 2**n

# 方法 2a：用遞迴 power2n(n-1)+power2n(n-1)
def power2n_2a(n):
    if n == 0:
        return 1
    return power2n_2a(n-1) + power2n_2a(n-1)

# 方法 2b：用遞迴 2*power2n(n-1)
def power2n_2b(n):
    if n == 0:
        return 1
    return 2 * power2n_2b(n-1)

# 方法 3：用遞迴+查表
_table = {}

def power2n_3(n):
    if n in _table:
        return _table[n]
    if n == 0:
        _table[0] = 1
        return 1
    _table[n] = power2n_3(n-1) + power2n_3(n-1)
    return _table[n]
