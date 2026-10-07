def sym_diff(expr, var='x'):
    # Base Case: 常數微分為 0
    if isinstance(expr, (int, float)):
        return 0
    # Base Case: 變數對自身微分為 1，對其他變數微分為 0
    if isinstance(expr, str):
        return 1 if expr == var else 0

    op = expr[0]
    
    if op == '+':
        # d/dx (u + v) = u' + v'
        return ('+', sym_diff(expr[1], var), sym_diff(expr[2], var))
        
    elif op == '-':
        # d/dx (u - v) = u' - v'
        return ('-', sym_diff(expr[1], var), sym_diff(expr[2], var))
        
    elif op == '*':
        # 乘法公式: d/dx (u * v) = u' * v + u * v'
        u, v = expr[1], expr[2]
        return ('+', ('*', sym_diff(u, var), v), ('*', u, sym_diff(v, var)))
        
    elif op == '/':
        # 除法公式: d/dx (u / v) = (u' * v - u * v') / (v^2)
        u, v = expr[1], expr[2]
        du, dv = sym_diff(u, var), sym_diff(v, var)
        return ('/', ('-', ('*', du, v), ('*', u, dv)), ('^', v, 2))
        
    elif op == '^':
        # 次方公式（冪法則與鏈鎖律）: d/dx (u^n) = n * u^(n-1) * u'
        u, n = expr[1], expr[2]
        return ('*', ('*', n, ('^', u, n - 1)), sym_diff(u, var))
        
    elif op == 'sin':
        # d/dx sin(u) = cos(u) * u'
        u = expr[1]
        return ('*', ('cos', u), sym_diff(u, var))
        
    elif op == 'cos':
        # d/dx cos(u) = -sin(u) * u'
        u = expr[1]
        return ('*', ('*', -1, ('sin', u)), sym_diff(u, var))

# 測試範例 1: d/dx (x * x + 3 * x)
expr1 = ('+', ('*', 'x', 'x'), ('*', 3, 'x'))
print("d/dx (x*x + 3*x) =", sym_diff(expr1))

# 測試範例 2: d/dx (x * sin(x))
expr2 = ('*', 'x', ('sin', 'x'))
print("d/dx (x * sin(x)) =", sym_diff(expr2))