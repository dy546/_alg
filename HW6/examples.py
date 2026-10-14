"""內建的 Lambda Calculus 範例程式。

範例分成兩層：
1. 巨集（macro）：有名字的「子程式」，輸入時可以用名字，展開後變成純 λ。
   例如輸入 add 2 3 會先展開成 (λm. λn. λf. λx. m f (n f x)) (λf. λx. f (f x)) (λf. λx. f (f (f x)))
2. 展示程式（demo）：一組可以直接跑、能看到完整計算過程的題目。

寫法說明（所有巨集都是純 lambda calculus，沒有偷用 Python 的加法）：
- Church boolean：真 = λx. λy. x（選第一個），假 = λx. λy. y（選第二個）
- Church numeral：數字 n = λf. λx. f^n x（把 f 套用 n 次）
- pair = λx. λy. λf. f x y，fst 取第一項，snd 取第二項
- Y combinator：Y = λf. (λx. f (x x)) (λx. f (x x))，做遞迴用
"""

try:
    from .lambdacalc import parse  # 當 HW6 被當成套件 import 時（from HW6.examples import ...）
except ImportError:
    from lambdacalc import parse   # 直接執行 python3 examples.py 時

# ───────────────────────────── 巨集表 ─────────────────────────────
# 輸入語法裡出現這些名字時，會先展開成右邊的純 λ 算式。

MACROS: dict[str, str] = {
    # ── identity / 基本 ──
    "id": r"λx. x",

    # ── Church booleans ──
    "true": r"λx. λy. x",
    "false": r"λx. λy. y",
    "and": r"λp. λq. p q p",
    "or": r"λp. λq. p p q",
    "not": r"λp. λa. λb. p b a",
    "if": r"λp. λa. λb. p a b",

    # ── pair（序對） ──
    "pair": r"λx. λy. λf. f x y",
    "fst": r"λp. p (λx. λy. x)",
    "snd": r"λp. p (λx. λy. y)",

    # ── Church numerals ──
    "0": r"λf. λx. x",
    "1": r"λf. λx. f x",
    "2": r"λf. λx. f (f x)",
    "3": r"λf. λx. f (f (f x))",
    "4": r"λf. λx. f (f (f (f x)))",
    "5": r"λf. λx. f (f (f (f (f x))))",
    "6": r"λf. λx. f (f (f (f (f (f x)))))",
    "succ": r"λn. λf. λx. f (n f x)",
    "add": r"λm. λn. λf. λx. m f (n f x)",
    "mul": r"λm. λn. λf. m (n f)",
    "pow": r"λm. λn. n m",
    "iszero": r"λn. n (λx. false) true",
    "pred": r"λn. λf. λx. n (λg. λh. h (g f)) (λu. x) (λu. u)",

    # ── recursion（Y combinator） ──
    "Y": r"λf. (λx. f (x x)) (λx. f (x x))",
    "fact": r"Y (λf. λn. if (iszero n) 1 (mul n (f (pred n))))",

    # ── 發散（不會終止） ──
    "omega": r"(λx. x x) (λx. x x)",
    "loop": r"Y (λr. λx. r x)",
}

# ───────────────────────────── 展示程式 ─────────────────────────────

DEMOS: dict[str, str] = {
    "identity": "id a",
    "beta-simple": r"(λx. x (x y)) z",
    "capture": r"(λx. λy. x) y",
    "and": "and true false",
    "or": "or false true",
    "not": "not true",
    "pair": "fst (pair a b)",
    "succ-2": "succ 2",
    "add-2-3": "add 2 3",
    "mul-2-3": "mul 2 3",
    "iszero-0": "iszero 0",
    "iszero-3": "iszero 3",
    "pow-2-3": "pow 2 3",
    "fact-1": "fact 1",
    "fact-2": "fact 2",
    "omega": "omega",
    "loop": "loop x",
}


def expand_macros(src: str) -> str:
    """把輸入裡出現的巨集名字展開成純 λ 算式。

    做法：反覆掃描 src，遇到巨集名字就換成「(巨集定義)」，
    直到沒有任何巨集名字剩下為止（因為巨集定義裡也可能用到別的巨集，
    例如 fact 用到 Y、if、iszero、mul、pred）。只替換名字本身，
    名字之間的空白會原樣保留，避免 a b 被黏成 ab。
    """
    import re
    token_re = re.compile(r"\d+|[A-Za-z_][A-Za-z0-9_']*")

    def once(s: str) -> str:
        return token_re.sub(
            lambda m: f"({MACROS[m.group()]})" if m.group() in MACROS else m.group(),
            s,
        )

    cur = src
    while True:
        nxt = once(cur)
        if nxt == cur:
            return cur
        cur = nxt


def parse_program(src: str):
    """剖析一段「程式」（可含巨集），回傳 (ast, 展開後的原始字串)。"""
    expanded = expand_macros(src)
    return parse(expanded), expanded


def all_demo_names() -> list[str]:
    return list(DEMOS.keys())


def demo_description(name: str) -> str:
    return DEMOS.get(name, "")
