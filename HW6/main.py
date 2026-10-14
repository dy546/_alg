"""HW6 Lambda Calculus 解譯器：示範主程式。

用法：
    python3 main.py              執行全部內建範例，逐步顯示 β-reduction
    python3 main.py add-2-3      只執行指定範例（可多個，用空白隔開）
    python3 main.py -i           互動模式（REPL），可輸入自己的算式
    python3 main.py --db         每個範例同時顯示 de Bruijn 版本

REPL 指令：
    :demos / :list   列出所有內建範例
    :normal          換成 normal order 策略（預設）
    :cbv             換成 call-by-value 策略
    :quit / :q       離開
"""

import sys

from lambdacalc import (
    parse_error, pretty, pretty_db, trace,
    to_debruijn, db_trace,
    recognize, set_color, green, yellow, red, cyan, dim,
)
from examples import parse_program, DEMOS, all_demo_names, expand_macros

MAX_STEPS = 1000


# ───────────────────────────── 逐步顯示 ─────────────────────────────

def show_trace(src: str, *, strategy: str = "normal", show_db: bool = False,
               max_steps: int = MAX_STEPS) -> None:
    """剖析 src（可含巨集），逐步印出完整的 β-reduction 過程。"""
    ast, expanded = parse_program(src)
    if expanded != src:
        print(f"{cyan('展開巨集後')}：{dim(expanded)}")

    steps, final, terminated = trace(ast, strategy, max_steps)
    if not steps:
        print(f"  {dim('（已經是 normal form，不用算）')}")
    elif terminated:
        for i, st in enumerate(steps, 1):
            _print_step(i, st)
    else:
        # 發散：只印前幾步跟最後一步，中間省略
        head, tail = 8, 3
        for i, st in enumerate(steps[:head], 1):
            _print_step(i, st)
        if len(steps) > head + tail:
            print(f"  {dim(f'…（中間省略 {len(steps) - head - tail} 步）…')}")
        for i, st in enumerate(steps[-tail:], len(steps) - tail + 1):
            _print_step(i, st)

    what = recognize(final)
    extra = f"  {yellow(f'≡ {what}')}" if what else ""
    if terminated:
        print(f"  {red('⇒')} {pretty(final)}{extra}  {dim(f'（共 {len(steps)} 步）')}")
    else:
        print(f"  {red(f'⚠ 超過 {max_steps} 步仍未停止（發散）')}")

    if show_db:
        show_db_trace(ast)


def _print_step(i: int, st) -> None:
    note = ""
    if st.alpha:
        pairs = "、".join(f"{old} → {new}" for old, new in st.alpha)
        note = f"  {dim(f'（α-改名：{pairs}）')}"
    print(f"  {green(f'[{i}]')} {pretty(st.after)}{note}")


def show_db_trace(ast) -> None:
    """把（封閉的）term 轉成 de Bruijn 表示法，顯示換算與計算過程。"""
    try:
        dbt = to_debruijn(ast)
    except ValueError as e:
        print(f"  {dim(f'（含自由變數，無法轉 de Bruijn：{e}）')}")
        return
    print(f"  {cyan('de Bruijn 版')}：{pretty_db(dbt)}")
    steps, final, terminated = db_trace(dbt, MAX_STEPS)
    for i, st in enumerate(steps[:3], 1):
        print(f"    {dim(f'[{i}]')} {pretty_db(st.after)}")
    if len(steps) > 3:
        print(f"    {dim('…')}")
    if terminated:
        print(f"    {dim(f'⇒ {pretty_db(final)}（共 {len(steps)} 步）')}")
    else:
        print(f"    {red(f'⚠ 超過 {MAX_STEPS} 步仍未停止（發散）')}")


# ───────────────────────────── 互動模式（REPL） ─────────────────────────────

def repl() -> None:
    strategy = "normal"
    print(f"{cyan('Lambda Calculus 解譯器')}（輸入 :help 看說明，:quit 離開）")
    print(f"目前策略：{yellow(strategy)}")
    while True:
        try:
            src = input("λ> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not src:
            continue
        if src in (":quit", ":q", "exit"):
            break
        if src in (":demos", ":list"):
            for name in all_demo_names():
                print(f"  {green(name):12s} {DEMOS[name]}")
            continue
        if src == ":normal":
            strategy = "normal"
            print(f"策略換成 {yellow('normal order')}")
            continue
        if src == ":cbv":
            strategy = "cbv"
            print(f"策略換成 {yellow('call-by-value')}")
            continue
        if src == ":help":
            print(__doc__)
            continue
        err = parse_error(expand_macros(src))
        if err:
            print(f"{red('剖析錯誤')}：{err}")
            continue
        show_trace(src, strategy=strategy)


# ───────────────────────────── 主程式 ─────────────────────────────

def main(argv: list[str]) -> int:
    set_color(sys.stdout.isatty())

    if "-i" in argv or "--interactive" in argv:
        repl()
        return 0

    show_db = "--db" in argv
    names = [a for a in argv[1:] if not a.startswith("-")]
    if not names:
        names = all_demo_names()
    else:
        unknown = [n for n in names if n not in DEMOS]
        if unknown:
            print(f"{red('未知範例')}：{', '.join(unknown)}")
            print(f"可用的範例：{', '.join(all_demo_names())}")
            return 1

    for name in names:
        print(f"\n{green('▶')} {name}  {dim(f'({DEMOS[name]})')}")
        show_trace(DEMOS[name], show_db=show_db)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
