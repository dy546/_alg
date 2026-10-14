"""語法剖析器：把字串轉成 AST（有名稱的版本）。

接受的語法（BNF）：

    term        := application
    application := atom+              ; 左結合（left associative）
    atom        := VAR | '(' term ')' | (λ | '\\') VAR '.' term

範例：
    λx. x               → Abs("x", Var("x"))
    λf. λx. f (f x)     → Abs("f", Abs("x", App(Var("f"), App(Var("f"), Var("x")))))
    (λx. x) y           → App(Abs("x", Var("x")), Var("y"))
    λx. x y             → Abs("x", App(Var("x"), Var("y")))   （body 盡量延伸）
"""

import re
from .terms import Var, Abs, App, Term

_TOKEN_RE = re.compile(
    r"""
      (?P<WS>\s+)
    | (?P<LAMBDA>λ|\\)
    | (?P<LPAREN>\()
    | (?P<RPAREN>\))
    | (?P<DOT>\.)
    | (?P<VAR>[A-Za-z_][A-Za-z0-9_']*)
    """,
    re.VERBOSE,
)


class ParseError(ValueError):
    """剖析失敗時丟出的例外。"""


def _tokenize(src: str):
    tokens = []
    pos = 0
    while pos < len(src):
        m = _TOKEN_RE.match(src, pos)
        if not m:
            raise ParseError(f"無法辨識的字元 {src[pos]!r}（位置 {pos}）")
        if m.lastgroup != "WS":
            tokens.append((m.lastgroup, m.group()))
        pos = m.end()
    return tokens


def parse(src: str) -> Term:
    """剖析一整串 lambda 語法，回傳 AST。剖析失敗會丟 ParseError。"""
    tokens = _tokenize(src)
    i = [0]
    t = _parse_application(tokens, i)
    if i[0] != len(tokens):
        kind, val = tokens[i[0]]
        raise ParseError(f"多餘的符號 {val!r}（位置 {i[0]}）")
    return t


def parse_error(src: str) -> str:
    """剖析失敗時把錯誤訊息轉成字串（方便 UI 顯示）。"""
    try:
        parse(src)
        return ""
    except ParseError as e:
        return str(e)


def _parse_application(tokens, i) -> Term:
    """application := atom+（左結合）。"""
    t = _parse_atom(tokens, i)
    while i[0] < len(tokens) and tokens[i[0]][0] in ("VAR", "LPAREN", "LAMBDA"):
        arg = _parse_atom(tokens, i)
        t = App(t, arg)
    return t


def _parse_atom(tokens, i) -> Term:
    if i[0] >= len(tokens):
        raise ParseError("意外的結尾：缺少運算式")
    kind, val = tokens[i[0]]
    i[0] += 1

    if kind == "VAR":
        return Var(val)

    if kind == "LPAREN":
        t = _parse_application(tokens, i)
        if i[0] >= len(tokens) or tokens[i[0]][0] != "RPAREN":
            raise ParseError("缺少右括號 ')'")
        i[0] += 1
        return t

    if kind == "LAMBDA":
        if i[0] >= len(tokens) or tokens[i[0]][0] != "VAR":
            raise ParseError("λ 後面必須接變數名稱，例如 λx. ...")
        name = tokens[i[0]][1]
        i[0] += 1
        if i[0] >= len(tokens) or tokens[i[0]][0] != "DOT":
            raise ParseError("λx 後面必須接 '.'，例如 λx. x")
        i[0] += 1
        body = _parse_application(tokens, i)
        return Abs(name, body)

    raise ParseError(f"不預期的符號 {val!r}")
