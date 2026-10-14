"""β-reduction 引擎：normal order（最左最外層）與 call-by-value。

計算過程追蹤：每執行一步 β-reduction 就記下
- 這一步消掉哪個 redex（(λx. M) N）
- 算出來的結果整句長什麼樣
- 有沒有因為避免變數捕捉而做的 α-改名

reduction 策略：
- normal：最左最外層（leftmost outermost）──這是 standard order，
  只要 term 有 normal form 就一定能算到，最適合「展示完整計算過程」。
- cbv：call-by-value──先把參數算成 value 再代入，對應多數程式語言。
"""

from dataclasses import dataclass, field
from .terms import Var, Abs, App, Term
from .normalize import substitute


@dataclass
class Step:
    """一步 reduction 的紀錄。"""
    kind: str                       # "β"（目前只有 β）
    before: Term                    # 這一步之前的整句
    after: Term                     # 這一步之後的整句
    redex: Term                     # 被消掉的 redex
    alpha: list = field(default_factory=list)  # [(舊名, 新名), ...] α-改名紀錄


def reduce1(t: Term, strategy: str = "normal") -> tuple[Term, Step] | None:
    """執行一步 reduction。

    回傳 (新整句, Step)，若已經是 normal form（沒有 redex）則回傳 None。
    """
    if isinstance(t, Var):
        return None

    if isinstance(t, Abs):
        # normal order 會進入 λ 的 body 裡面繼續找 redex
        if strategy == "cbv":
            return None  # call-by-value 不計算 λ 裡面
        r = reduce1(t.body, strategy)
        if r:
            new_body, step = r
            return (Abs(t.param, new_body), step)
        return None

    # t 是 App
    if isinstance(t.f, Abs):
        # β-redex：(λx. M) N  →  M[x := N]
        body2, renames = substitute(t.f.body, t.f.param, t.arg)
        return (body2, Step("β", t, body2, t, renames))

    if strategy == "cbv":
        # call-by-value：參數先算成 value，再算函數
        r = reduce1(t.arg, strategy)
        if r:
            new_arg, step = r
            return (App(t.f, new_arg), step)
        r = reduce1(t.f, strategy)
        if r:
            new_f, step = r
            return (App(new_f, t.arg), step)
        return None

    # normal order：先找函數位置的最左最外 redex
    r = reduce1(t.f, strategy)
    if r:
        new_f, step = r
        return (App(new_f, t.arg), step)
    r = reduce1(t.arg, strategy)
    if r:
        new_arg, step = r
        return (App(t.f, new_arg), step)
    return None


def trace(t: Term, strategy: str = "normal", max_steps: int = 100):
    """逐步 reduction，產生完整的計算過程。

    回傳 (steps, final_term, terminated)：
    - steps：每個元素是 Step（每次的 before 就是上一次的 after）
    - final_term：停下來時的整句（normal form，或因為步數上限而停住）
    - terminated：True 表示算到 normal form；False 表示超過步數上限
      （可能是發散不終止的程式，例如 Ω）
    """
    steps: list[Step] = []
    cur = t
    for _ in range(max_steps):
        r = reduce1(cur, strategy)
        if r is None:
            return steps, cur, True
        new_cur, step = r
        steps.append(step)
        cur = new_cur
    return steps, cur, False


def evaluate(t: Term, strategy: str = "normal", max_steps: int = 100):
    """一步到位的求值，回傳 (final_term, n_steps, terminated)。"""
    steps, final, terminated = trace(t, strategy, max_steps)
    return final, len(steps), terminated
