"""Lambda Calculus 解譯器套件。

包含兩種版本：
- 有名稱（named）: λx. x、λf. λx. f (f x) ……
- 沒名稱（de Bruijn indices）: λ. 0、λ. λ. 1 (1 0) ……

兩種版本都可以逐步顯示完整的 β-reduction 計算過程。
"""

from .terms import Var, Abs, App
from .parser import parse, parse_error
from .normalize import free_vars, substitute
from .eval import reduce1, trace, evaluate, Step
from .debruijn import (
    DBVar, DBAbs, DBApp,
    to_debruijn, from_debruijn,
    parse_debruijn, db_reduce1, db_trace,
)
from .pretty import (
    pretty, pretty_db, db_pretty_named,
    recognize, term_to_unicode,
    set_color, red, green, yellow, cyan, dim,
)

__all__ = [
    "Var", "Abs", "App",
    "parse", "parse_error",
    "free_vars", "substitute",
    "reduce1", "trace", "evaluate", "Step",
    "DBVar", "DBAbs", "DBApp",
    "to_debruijn", "from_debruijn",
    "parse_debruijn", "db_reduce1", "db_trace",
    "pretty", "pretty_db", "db_pretty_named",
    "recognize", "term_to_unicode",
    "set_color", "red", "green", "yellow", "cyan", "dim",
]
