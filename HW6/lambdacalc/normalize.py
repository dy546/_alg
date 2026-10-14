"""自由變數、α-conversion（改名）、capture-avoiding substitution（避免變數捕捉的替換）。

β-reduction 的定義是：

    (λx. M) N  ⟶β  M[x := N]

其中 M[x := N] 是「把 M 裡面所有 *自由的* x 換成 N」。
但直接文字替換會出事（變數捕捉，variable capture）：

    (λx. λy. x) y  →  若直接替換：λy. y   ← 錯！這個 y 變成被綁住了
    正確結果應該是：λy'. y（先把內層的 y 改名）

所以替換必須是 capture-avoiding：當 λy. 的 body 會被塞進含有自由 y 的 N 時，
先幫 y 改名成一個全新的名字。本模組會記錄每一次的改名（renames），
讓解譯器可以把「α-改名」也顯示在計算過程裡。
"""

from .terms import Var, Abs, App, Term


def free_vars(t: Term) -> set[str]:
    """收集 term 裡所有的自由變數。"""
    if isinstance(t, Var):
        return {t.name}
    if isinstance(t, Abs):
        return free_vars(t.body) - {t.param}
    return free_vars(t.f) | free_vars(t.arg)


def fresh_name(name: str, avoid: set[str]) -> str:
    """產生一個不在 avoid 集合裡的新名字：y → y' → y'' → ……"""
    if name not in avoid:
        return name
    i = 1
    while True:
        cand = name + "'" * i
        if cand not in avoid:
            return cand
        i += 1


def substitute(t: Term, x: str, s: Term) -> tuple[Term, list[tuple[str, str]]]:
    """計算 t[x := s]（capture-avoiding）。

    回傳 (結果, renames)，renames = [(舊名, 新名), ...] 記錄過程中做的 α-改名。
    """
    renames: list[tuple[str, str]] = []
    result = _sub(t, x, s, free_vars(s), renames)
    return result, renames


def _sub(t: Term, x: str, s: Term, s_free: set[str], renames) -> Term:
    if isinstance(t, Var):
        return s if t.name == x else t

    if isinstance(t, App):
        return App(_sub(t.f, x, s, s_free, renames),
                   _sub(t.arg, x, s, s_free, renames))

    # t 是 Abs
    if t.param == x:
        # x 在這裡被重新綁定，遮蔽了外面的 x，不用替換
        return t
    if t.param in s_free:
        # 變數捕捉！先把 binder 改名成全新的名字
        z = fresh_name(t.param, free_vars(t.body) | s_free | {x})
        renames.append((t.param, z))
        body2 = _sub(t.body, t.param, Var(z), s_free, renames)
        return Abs(z, _sub(body2, x, s, s_free, renames))
    return Abs(t.param, _sub(t.body, x, s, s_free, renames))


def rename(t: Term, old: str, new: str) -> Term:
    """單純的 α-改名（不觸發新的改名紀錄）。new 必須是全新的名字。"""
    if isinstance(t, Var):
        return Var(new) if t.name == old else t
    if isinstance(t, App):
        return App(rename(t.f, old, new), rename(t.arg, old, new))
    if t.param == old:
        return t
    return Abs(t.param, rename(t.body, old, new))
