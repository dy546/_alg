"""Lambda Term 的 AST（有名稱的版本）。

三種節點：
- Var(name)           變數，例如 Var("x")
- Abs(param, body)    λ 抽象（lambda abstraction），例如 Abs("x", Var("x"))
- App(f, arg)         函數套用（application），例如 App(Abs("x", Var("x")), Var("y"))

用 frozen dataclass 表示：不可變、可用 == 比較、可放進 set/dict。
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Var:
    name: str


@dataclass(frozen=True)
class Abs:
    param: str
    body: "Term"


@dataclass(frozen=True)
class App:
    f: "Term"
    arg: "Term"


Term = Var | Abs | App
