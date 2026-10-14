# HW6 — Lambda Calculus Interpreter

A pure-Python lambda calculus interpreter with step-by-step β-reduction,
in two flavors: named terms (`λx. x`) and nameless de Bruijn indices
(`λ. 0`). Everything — booleans, numerals, arithmetic, pairs, recursion —
is built from raw λ-terms; no Python arithmetic is used.

## Files

| File | Description |
|---|---|
| `lambdacalc/` | The interpreter package |
| `lambdacalc/terms.py` | Named-term AST: `Var`, `Abs`, `App` |
| `lambdacalc/parser.py` | Parser for named syntax (`λx. x`, `\x. x`) |
| `lambdacalc/normalize.py` | Free variables, α-conversion, capture-avoiding substitution |
| `lambdacalc/eval.py` | β-reduction engine (normal order and call-by-value) with step tracing |
| `lambdacalc/debruijn.py` | de Bruijn indices: shift, substitution, reduction, parser, conversion |
| `lambdacalc/pretty.py` | Minimal-parenthesis pretty-printer, ANSI colors, result recognition |
| `examples.py` | Named macros (Church booleans/numerals, pairs, Y combinator) and demo programs |
| `main.py` | Demo runner + interactive REPL |

## Usage

```bash
cd HW6
python3 main.py               # run all built-in demos step by step
python3 main.py add-2-3       # run specific demos
python3 main.py --db          # also show the de Bruijn version of each demo
python3 main.py -i            # interactive REPL
```

REPL commands: `:demos` lists the built-ins, `:normal` / `:cbv` switch the
reduction strategy, `:quit` exits. Terms may use any macro name from
`examples.py`.

As a library:

```python
from lambdacalc import parse, pretty, trace
from examples import parse_program

ast, _ = parse_program("add 2 3")      # macro expansion + parsing
steps, final, terminated = trace(ast)  # normal-order reduction
print(pretty(final))                   # λf. λx. f (f (f (f (f x))))
```

## Syntax

```
term        := application
application := atom+              ; left associative
atom        := VAR | '(' term ')' | (λ | '\') VAR '.' term
```

`λx. x y` parses as `λx. (x y)` (the body extends as far as possible).

## Macros

Input may use the named macros from `examples.py`; they are expanded
recursively into pure λ-terms before parsing (so `fact` expands `Y`, `if`,
`iszero`, `mul`, `pred`, and the numerals too):

| Macro | Meaning |
|---|---|
| `id` | identity `λx. x` |
| `true`, `false` | Church booleans `λx. λy. x` / `λx. λy. y` |
| `and`, `or`, `not`, `if` | Church boolean logic |
| `pair`, `fst`, `snd` | pairs |
| `0` … `6` | Church numerals |
| `succ`, `add`, `mul`, `pow`, `iszero`, `pred` | Church arithmetic |
| `Y` | Y combinator for recursion |
| `fact` | factorial via `Y` |
| `omega`, `loop` | divergent (non-terminating) terms |

## Built-in demos

| Demo | Program | Result |
|---|---|---|
| `identity` | `id a` | `a` |
| `beta-simple` | `(λx. x (x y)) z` | `z (z y)` |
| `capture` | `(λx. λy. x) y` | `λy'. y` (α-renamed) |
| `and` | `and true false` | false |
| `or` | `or false true` | true |
| `not` | `not true` | false |
| `pair` | `fst (pair a b)` | `a` |
| `succ-2` | `succ 2` | 3 |
| `add-2-3` | `add 2 3` | 5 |
| `mul-2-3` | `mul 2 3` | 6 |
| `iszero-0` / `iszero-3` | `iszero 0` / `iszero 3` | true / false |
| `pow-2-3` | `pow 2 3` | 8 |
| `fact-1` / `fact-2` | `fact 1` / `fact 2` | 1 / 2 |
| `omega`, `loop` | — | diverges |

## How it works

- **Reduction strategy.** `normal` (default) reduces the leftmost-outermost
  redex, so a normal form is found whenever one exists; `cbv` evaluates
  arguments first (like most programming languages).
- **Capture avoidance.** Substitution `M[x := N]` renames bound variables
  when `N` would capture them, and every α-rename is recorded and shown in
  the trace, e.g. `(λx. λy. x) y ⟶ λy'. y`.
- **de Bruijn indices.** `λx. λy. x y` becomes `λ. λ. 1 0`. β-reduction is
  then just index shifting plus substituting index 0 — no names, no capture
  problems. `to_debruijn` / `from_debruijn` convert between the two
  representations, and `parse_debruijn` parses nameless syntax (`λ. λ. 1 0`).
- **Recognition.** `pretty.recognize` identifies normal forms: Church
  numerals, booleans, identity, and pairs, so `add 2 3` prints
  `≡ Church 數字 5` next to the raw term.

## Design notes

- Terms are frozen dataclasses (`Var`, `Abs`, `App`), so they are immutable,
  comparable with `==`, and hashable.
- `trace` returns `(steps, final, terminated)`; `terminated=False` means the
  step limit was hit, i.e. the term likely diverges (`omega`, `loop`).
- The parser raises `ParseError` (a `ValueError`) with the position of the
  error; `main.py` and the REPL catch it and print a friendly message.
