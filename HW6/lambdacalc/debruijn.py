"""沒名稱的版本：de Bruijn indices。

de Bruijn 表示法（1972）把「變數名稱」換成「數字」，數字表示
「往上數第幾個 λ 綁住我」：

    有名稱       沒名稱（de Bruijn）
    λx. x        λ. 0
    λx. λy. x    λ. λ. 1
    λx. λy. y    λ. λ. 0
    λx. λy. x y  λ. λ. 1 0

好處：不用管變數名稱、不會發生變數捕捉，α-equivalent 的 term
（只差名字）在 de Bruijn 下長得一模一樣。β-reduction 只需要
「位移（shift）」跟「替換 index 0」兩個動作，非常適合寫解譯器。

β-reduction（de Bruijn 版）:
    (λ. M) N  ⟶β  shift_down(subst(M, 0, shift_up(N, 1)))

其中
- shift_up(N, 1)：把 N 裡所有 index 加 1（因為 N 要進到多一層的環境）
- subst(M, 0, ...)：把 M 裡面 index 0 的位置換掉（index 0 就是最內層 λ 綁的）
- shift_down(...)：把結果全部 index 減 1（因為最外層那個 λ 被消掉了）
"""

from dataclasses import dataclass
from .terms import Var, Abs, App, Term
from .eval import Step


@dataclass(frozen=True)
class DBVar:
    index: int


@dataclass(frozen=True)
class DBAbs:
    body: "DBTerm"


@dataclass(frozen=True)
class DBApp:
    f: "DBTerm"
    arg: "DBTerm"


DBTerm = DBVar | DBAbs | DBApp


# ───────────────────────────── 位移（shift） ─────────────────────────────

def db_shift(t: DBTerm, d: int, cutoff: int = 0) -> DBTerm:
    """把所有 index >= cutoff 的變數加上 d。

    cutoff 是「保護線」：進到一層 λ 裡面時 cutoff 要 +1，
    因為裡面的 index 0 屬於更內層的 binder，不能被移動。
    """
    if isinstance(t, DBVar):
        return DBVar(t.index + d) if t.index >= cutoff else t
    if isinstance(t, DBAbs):
        return DBAbs(db_shift(t.body, d, cutoff + 1))
    return DBApp(db_shift(t.f, d, cutoff), db_shift(t.arg, d, cutoff))


# ───────────────────────────── 替換（substitution） ─────────────────────────────

def db_subst(t: DBTerm, j: int, s: DBTerm) -> DBTerm:
    """把 t 裡面所有「自由的 index j」換成 s。

    進到 λ 裡面時 j 跟 s 都要 +1（因為環境多了一層）。
    """
    if isinstance(t, DBVar):
        return s if t.index == j else t
    if isinstance(t, DBAbs):
        return DBAbs(db_subst(t.body, j + 1, db_shift(s, 1, 0)))
    return DBApp(db_subst(t.f, j, s), db_subst(t.arg, j, s))


def db_subst_top(s: DBTerm, t: DBTerm) -> DBTerm:
    """替換最外層的 index 0（β-reduction 用）。"""
    return db_shift(db_subst(t, 0, db_shift(s, 1, 0)), -1, 0)


# ───────────────────────────── β-reduction ─────────────────────────────

def db_reduce1(t: DBTerm) -> tuple[DBTerm, Step] | None:
    """de Bruijn 版的一步 normal-order reduction，回傳 (新整句, Step)。"""
    if isinstance(t, DBVar):
        return None
    if isinstance(t, DBAbs):
        r = db_reduce1(t.body)
        if r:
            new_body, step = r
            return (DBAbs(new_body), step)
        return None
    # DBApp
    if isinstance(t.f, DBAbs):
        # (λ. M) N  →  shift_down( subst(M, 0, shift_up(N)) )
        new_body = db_subst_top(t.arg, t.f.body)
        return (new_body, Step("β", t, new_body, t, []))
    r = db_reduce1(t.f)
    if r:
        new_f, step = r
        return (DBApp(new_f, t.arg), step)
    r = db_reduce1(t.arg)
    if r:
        new_arg, step = r
        return (DBApp(t.f, new_arg), step)
    return None


def db_trace(t: DBTerm, max_steps: int = 100):
    """逐步 reduction，回傳 (steps, final, terminated)。"""
    steps = []
    cur = t
    for _ in range(max_steps):
        r = db_reduce1(cur)
        if r is None:
            return steps, cur, True
        new_cur, step = r
        steps.append(step)
        cur = new_cur
    return steps, cur, False


# ───────────────────── 有名稱 ↔ 沒名稱 互換 ─────────────────────

def to_debruijn(t: Term, env: list[str] | None = None) -> DBTerm:
    """有名稱 → de Bruijn。env 記錄目前可見的 binder 名字（最內層在前）。"""
    if env is None:
        env = []
    if isinstance(t, Var):
        try:
            return DBVar(env.index(t.name))
        except ValueError:
            raise ValueError(
                f"自由變數 {t.name!r} 無法轉成 de Bruijn index"
                f"（封閉 term 才能完全轉換，請先把它包進 λ 裡）")
    if isinstance(t, Abs):
        return DBAbs(to_debruijn(t.body, [t.param] + env))
    return DBApp(to_debruijn(t.f, env), to_debruijn(t.arg, env))


def from_debruijn(t: DBTerm, names: list[str] | None = None,
                  env: list[str] | None = None) -> Term:
    """de Bruijn → 有名稱（用 names 當作 binder 的名字，自動擴充）。"""
    if names is None:
        names = ["x", "y", "z", "u", "v", "w", "a", "b", "c"]
    if env is None:
        env = []
    if isinstance(t, DBVar):
        if t.index >= len(env):
            # index 超出環境：當成自由變數，取名 f0, f1, ...
            return Var(f"f{t.index - len(env)}")
        return Var(env[-(t.index + 1)])
    if isinstance(t, DBAbs):
        depth = len(env)
        name = names[depth % len(names)] if names else f"v{depth}"
        if depth >= len(names):
            name = f"v{depth}"
        return Abs(name, from_debruijn(t.body, names, env + [name]))
    return App(from_debruijn(t.f, names, env),
               from_debruijn(t.arg, names, env))


# ───────────────────────────── 剖析（沒名稱語法） ─────────────────────────────

def parse_debruijn(src: str) -> DBTerm:
    """剖析 de Bruijn 語法：λ . body、數字、（括號）、application。

    範例：λ. λ. 1 0、 (λ. 0) (λ. 0)
    """
    import re
    token_re = re.compile(
        r"""
          (?P<WS>\s+)
        | (?P<LAMBDA>λ|\\)
        | (?P<LPAREN>\()
        | (?P<RPAREN>\))
        | (?P<DOT>\.)
        | (?P<INDEX>\d+)
        """,
        re.VERBOSE,
    )
    tokens = []
    pos = 0
    while pos < len(src):
        m = token_re.match(src, pos)
        if not m:
            raise ValueError(f"無法辨識的字元 {src[pos]!r}（位置 {pos}）")
        if m.lastgroup != "WS":
            tokens.append((m.lastgroup, m.group()))
        pos = m.end()

    i = [0]

    def app():
        t = atom()
        while i[0] < len(tokens) and tokens[i[0]][0] in ("INDEX", "LPAREN", "LAMBDA"):
            t = DBApp(t, atom())
        return t

    def atom():
        if i[0] >= len(tokens):
            raise ValueError("意外的結尾：缺少運算式")
        kind, val = tokens[i[0]]
        i[0] += 1
        if kind == "INDEX":
            return DBVar(int(val))
        if kind == "LPAREN":
            t = app()
            if i[0] >= len(tokens) or tokens[i[0]][0] != "RPAREN":
                raise ValueError("缺少右括號 ')'")
            i[0] += 1
            return t
        if kind == "LAMBDA":
            if i[0] >= len(tokens) or tokens[i[0]][0] != "DOT":
                raise ValueError("λ 後面必須接 '.'，例如 λ. 0")
            i[0] += 1
            return DBAbs(app())
        raise ValueError(f"不預期的符號 {val!r}")

    t = app()
    if i[0] != len(tokens):
        raise ValueError(f"多餘的符號 {tokens[i[0]][1]!r}")
    return t
