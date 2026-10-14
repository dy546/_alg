"""漂亮的列印：最少括號、ANSI 顏色、常見 term 的辨識。

- pretty(t)：有名稱版，例如 (λx. x) y
- pretty_db(t)：de Bruijn 版，例如 (λ. 0) 0
- db_pretty_named(t)：de Bruijn term 用「重建的名字」顯示，方便閱讀
- recognize(t)：把結果辨識成常見的東西：
    真/假（Church boolean）、Church 數字 0~n、identity、pair ……
"""

from .terms import Var, Abs, App, Term
from .debruijn import DBVar, DBAbs, DBApp, DBTerm, from_debruijn


# ───────────────────────────── 最少括號的列印 ─────────────────────────────

def pretty(t: Term) -> str:
    if isinstance(t, Var):
        return t.name
    if isinstance(t, Abs):
        return f"λ{t.param}. {pretty(t.body)}"
    # App：左邊如果是 λ 要加括號；右邊如果不是變數要加括號
    left = pretty(t.f)
    if isinstance(t.f, Abs):
        left = f"({left})"
    right = pretty(t.arg)
    if not isinstance(t.arg, Var):
        right = f"({right})"
    return f"{left} {right}"


def pretty_db(t: DBTerm) -> str:
    if isinstance(t, DBVar):
        return str(t.index)
    if isinstance(t, DBAbs):
        return f"λ. {pretty_db(t.body)}"
    left = pretty_db(t.f)
    if isinstance(t.f, DBAbs):
        left = f"({left})"
    right = pretty_db(t.arg)
    if not isinstance(t.arg, DBVar):
        right = f"({right})"
    return f"{left} {right}"


def db_pretty_named(t: DBTerm) -> str:
    """de Bruijn term 用重建的名稱顯示（只為了好讀，index 仍然正確）。"""
    return pretty(from_debruijn(t))


# ───────────────────────────── ANSI 顏色 ─────────────────────────────

_RED = "\033[31;1m"
_GREEN = "\033[32;1m"
_YELLOW = "\033[33;1m"
_CYAN = "\033[36m"
_DIM = "\033[2m"
_RESET = "\033[0m"

_color_on = False


def set_color(on: bool):
    global _color_on
    _color_on = on


def _c(code: str, s: str) -> str:
    return f"{code}{s}{_RESET}" if _color_on else s


def red(s): return _c(_RED, s)
def green(s): return _c(_GREEN, s)
def yellow(s): return _c(_YELLOW, s)
def cyan(s): return _c(_CYAN, s)
def dim(s): return _c(_DIM, s)


# ───────────────────────────── 常見 term 辨識 ─────────────────────────────

def _church_numeral(t: Term) -> int | None:
    """如果是 Church numeral λf. λx. f^n x，回傳 n。"""
    if not isinstance(t, Abs):
        return None
    if not isinstance(t.body, Abs):
        return None
    f, body = t.param, t.body
    x = body.param
    cur = body.body
    n = 0
    while True:
        if isinstance(cur, Var) and cur.name == x:
            return n
        if (isinstance(cur, App) and isinstance(cur.f, Var)
                and cur.f.name == f):
            n += 1
            cur = cur.arg
            continue
        return None


def _church_bool(t: Term) -> str | None:
    """Church boolean：true = λx. λy. x，false = λx. λy. y。"""
    if (isinstance(t, Abs) and isinstance(t.body, Abs)):
        x, body = t.param, t.body
        y = body.param
        inner = body.body
        if isinstance(inner, Var):
            if inner.name == x:
                return "true（真）"
            if inner.name == y:
                return "false（假）"
    return None


def recognize(t: Term) -> str | None:
    """辨識結果 term 是什麼，回傳人話描述，認不出來回傳 None。"""
    n = _church_numeral(t)
    if n is not None:
        if n == 0:
            return "Church 數字 0"
        if n == 1:
            return "Church 數字 1"
        return f"Church 數字 {n}"
    b = _church_bool(t)
    if b is not None:
        return f"Church boolean：{b}"
    if isinstance(t, Abs) and isinstance(t.body, Var) and t.param == t.body.name:
        return "identity（身分函數 λx. x）"
    if isinstance(t, App) and isinstance(t.f, Abs) and isinstance(t.arg, Abs):
        return "pair（序對）"
    return None


def term_to_unicode(s: str) -> str:
    """把輸出裡的 ASCII 箭頭換成好看一點的箭頭（網頁顯示用）。"""
    return s.replace("->", "⟶")
