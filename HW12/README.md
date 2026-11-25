# HW12 — Computational Theory: Machines, Grammars, λ-Calculus, and Limits

> **One file, four models, one question: what can be computed?**
>
> This directory contains only this README. The Python blocks in each section
> are meant to be run together; every runnable block was executed with
> Python 3.12, and the outputs shown are from those runs.

| Requested topic | Section | What it answers |
|---|---|---|
| Finite state machine | [§1](#1-finite-state-machines) | What can a machine with **finite memory** decide? |
| Grammar | [§2](#2-grammars-and-the-chomsky-hierarchy) | How do we **generate** and **parse** structured strings? |
| Lambda calculus | [§3](#3-lambda-calculus-functions-as-computation) | What can **pure functions and substitution** compute? |
| Turing machine | [§4](#4-turing-machines-and-the-limits-of-computation) | What can **any algorithm** compute — and what can it not? |

**A note on terminology.** The assignment's *"downtime issues"* is best read
as the **halting problem** (停機問題): does a machine eventually stop?
*"Church–Turing arguments"* means the **Church–Turing thesis** (邱奇–圖靈論題).
*"Chomsky class"* means the **Chomsky hierarchy** (Type 0–3).
*"Closed package"* is read as **closure**; [§3.4](#34-closures-in-programming-languages-the-other-closed-package)
separates the four different things called "closure" in this subject.

**In one line each.**

* **DFA** — a machine with finite memory; it recognizes exactly the regular
  languages.
* **CFG** — a context-free grammar; its recognizer, the PDA, adds a stack to
  a DFA, and the Chomsky hierarchy classifies grammars by production shape.
* **λ-calculus** — functions and substitution; in implementations, closures
  package code with an environment, and the Y combinator creates recursion;
  it is Turing-complete.
* **Turing machine** — a finite control plus an unbounded tape; it defines
  computability, and the halting problem shows its limit.

---

## Contents

- [0. The big picture](#0-the-big-picture)
- [1. Finite state machines](#1-finite-state-machines)
- [2. Grammars and the Chomsky hierarchy](#2-grammars-and-the-chomsky-hierarchy)
- [3. Lambda calculus: functions as computation](#3-lambda-calculus-functions-as-computation)
- [4. Turing machines and the limits of computation](#4-turing-machines-and-the-limits-of-computation)
- [5. Putting the four models together](#5-putting-the-four-models-together)
- [6. Common misconceptions](#6-common-misconceptions)
- [7. Glossary (English–中文)](#7-glossary-english中文)
- [8. References](#8-references)
- [9. About this document](#9-about-this-document)

---

## 0. The big picture

The four topics look unrelated, but they are four points on one ladder. The
rung is determined mostly by **how much memory the machine has** (the
DCFL/CFL split is about determinism, not memory):

```
   regular  ⊊  DCFL  ⊊  CFL  ⊊  CSL  ⊊  recursive  ⊊  RE
     DFA        DPDA     PDA      LBA       halting TM      TM
   no memory   stack    stack   linear      tape, must      tape, may
               (det.)   (nondet.) tape      always halt     loop forever
```

Every `⊊` is a **strict** inclusion: there is a language at each level that
cannot be recognized at the level below.

| Model | Memory | Language class | Typical use |
|---|---|---|---|
| **DFA** | one state from a finite set | regular | lexers, protocols, regex |
| **PDA** | a stack (last-in, first-out) | context-free | parsers, bracket matching |
| **LBA** | a tape as long as the input | context-sensitive | constrained parsing |
| **TM** | an unbounded tape | recursively enumerable | general computation |
| **λ-calculus** | none — only rewriting | Turing-complete (same as TM) | functional programming, logic |

The two ends are the most important:

* A **DFA cannot count without bound**. It can remember "I have seen three
  zeros", but not "I have seen *n* zeros, and now I need *n* ones".
* A **Turing machine can do anything an algorithm can do** — and that very
  power makes some questions about it impossible to answer by algorithm.

The rest of this document explains each rung, then shows how they meet.

---

## 1. Finite state machines

### 1.1 What "finite memory" means

A **finite state machine** (FSM, 有限狀態機) reads an input string one symbol
at a time. Its entire memory is *which state it is in*, and there are only
finitely many states. It has no stack, no tape, no counter, and no variables.

Two consequences follow immediately:

1. A run always terminates: after reading `n` symbols, the machine has taken
   exactly `n` steps. It cannot loop while reading.
2. It cannot solve a problem that needs unbounded counting or unbounded
   nesting. "Count the zeros and check that the number of ones is equal" is
   beyond it, because the required count is unbounded.

The most important version is the **deterministic finite automaton** (DFA,
確定性有限自動機). "Deterministic" means that for each state and input symbol
there is exactly one next state.

### 1.2 Formal definition of a DFA

A DFA is a 5-tuple

```
M = (Q, Σ, δ, q0, F)
```

| Symbol | Meaning |
|---|---|
| `Q` | a finite, non-empty set of **states** |
| `Σ` | a finite **alphabet** (the input symbols) |
| `δ` | the **transition function**, `δ : Q × Σ → Q` |
| `q0` | the **start state**, `q0 ∈ Q` |
| `F` | the set of **accepting states**, `F ⊆ Q` |

`δ` is a *total* function: every state-symbol pair has a next state. A DFA
never gets stuck. (Some books allow a partial `δ`; a missing transition then
means "reject". The two definitions are equivalent.)

The machine starts in `q0`, reads the input left to right, and after the last
symbol accepts the string iff it is in a state from `F`.

### 1.3 State transitions

The transition function can be written in three equivalent ways:

1. **As a function:** `δ(q0, '0') = q1`.
2. **As a table:** rows are states, columns are symbols.
3. **As a graph:** states are nodes, transitions are labelled arrows.

**Running example.** Let

```
L = { w ∈ {0,1}* : w ends with 01 }.
```

The DFA needs to remember only the longest suffix of the input seen so far
that is a prefix of `01`. There are three such prefixes: `ε` (nothing useful),
`0`, and `01` (accept). That gives three states:

| State | Meaning | on `0` | on `1` |
|---|---|---|---|
| `q0` | no useful suffix | `q1` | `q0` |
| `q1` | last symbol is `0` | `q1` | `q2` |
| `q2` | last two symbols are `01` (accept) | `q1` | `q0` |

```
             1
        ┌─────────┐
        │         ▼
   ──► (q0) ──0──► (q1) ──1──► ((q2))
         ▲           │  ▲         │
         │           └──┘         │
         │            0           │
         └────────── 1 ───────────┘
```

The self-loop on `q0` labelled `1` says "a `1` destroys any partial match".
The self-loop on `q1` labelled `0` says "a `0` keeps us waiting for a `1`".
The arrow `q2 --1--> q0` says "after `01`, a `1` leaves only the suffix `1`,
which is not a prefix of `01`". The arrow `q2 --0--> q1` is not drawn
separately; the table says it goes back to `q1`.

The **extended transition function** `δ* : Q × Σ* → Q` is defined recursively:

```
δ*(q, ε)   = q
δ*(q, xa)  = δ(δ*(q, x), a)        for x ∈ Σ*, a ∈ Σ
```

In words: process the string one symbol at a time, starting from `q`. The
language of the machine is

```
L(M) = { w ∈ Σ* : δ*(q0, w) ∈ F }.
```

### 1.4 A DFA in Python

The transition function is just a dictionary. The `run` method is `δ*`:

```python
class DFA:
    def __init__(self, states, alphabet, delta, start, accept):
        self.states = set(states)
        self.alphabet = set(alphabet)
        self.delta = dict(delta)
        self.start = start
        self.accept = set(accept)

    def run(self, word, trace=False):
        state = self.start
        path = [state]
        for symbol in word:
            if symbol not in self.alphabet:
                raise ValueError(f"symbol {symbol!r} is not in the alphabet")
            state = self.delta[(state, symbol)]
            path.append(state)
        accepted = state in self.accept
        return (accepted, path) if trace else accepted


ENDS01 = DFA(
    states={"q0", "q1", "q2"},
    alphabet={"0", "1"},
    delta={
        ("q0", "0"): "q1", ("q0", "1"): "q0",
        ("q1", "0"): "q1", ("q1", "1"): "q2",
        ("q2", "0"): "q1", ("q2", "1"): "q0",
    },
    start="q0",
    accept={"q2"},
)

print(ENDS01.run("1101", trace=True))
print(ENDS01.run("1110", trace=True))
```

Output:

```text
(True, ['q0', 'q0', 'q0', 'q1', 'q2'])
(False, ['q0', 'q0', 'q0', 'q0', 'q1'])
```

The trace is the sequence of states *including the start state*. For `1101`
the machine ends in `q2`, so it accepts; for `1110` it ends in `q1`, so it
rejects.

**A second example: divisibility by 3.** Read the input as a binary number,
most significant bit first. The state is the remainder modulo 3, and

```
δ(qi, b) = q(2i + b) mod 3.
```

```python
MOD3 = DFA(
    states={0, 1, 2},
    alphabet={"0", "1"},
    delta={(r, b): (2 * r + int(b)) % 3 for r in range(3) for b in "01"},
    start=0,
    accept={0},
)

print(MOD3.run("1001", trace=True))   # 9  = 0 mod 3
print(MOD3.run("101",  trace=True))   # 5  = 2 mod 3
```

```text
(True, [0, 1, 2, 1, 0])
(False, [0, 1, 2, 2])
```

The state is the whole "memory" of the machine: after reading `1001`, being
in state `0` means "the number read so far is divisible by 3".

### 1.5 Regular languages and their limits

A language is **regular** (正規語言) iff some DFA accepts it. **Kleene's
theorem** says the following three descriptions are equally powerful:

```
DFA  ≡  NFA  ≡  regular expression
```

Regular languages are closed under union, intersection, complement,
concatenation, Kleene star, reversal, and difference. Membership, emptiness,
finiteness, and equivalence are all decidable.

**The pumping lemma** gives a necessary condition. If `L` is regular, there
is a number `p` (the pumping length) such that every `w ∈ L` with `|w| ≥ p`
can be written

```
w = x y z,     |xy| ≤ p,     |y| ≥ 1,
```

and `x y^i z ∈ L` for every `i ≥ 0`. Intuitively, a DFA with `p` states must
repeat a state while reading the first `p` symbols; the loop `y` can be
repeated or removed without leaving the language.

**Example: `{0^n 1^n}` is not regular.** Suppose it were, with pumping length
`p`, and take `w = 0^p 1^p`. Any split `w = xyz` with `|xy| ≤ p` has
`y = 0^k` for some `k ≥ 1`. Pumping twice gives `0^(p+k) 1^p`, which has more
zeros than ones — not in the language. Contradiction. Therefore no DFA can
check "equal numbers of zeros and ones", because that requires unbounded
counting.

The same argument shows that balanced parentheses, `{a^n b^n}`, and "the
number of `(` equals the number of `)`" are not regular.

**NFA vs DFA.** A **nondeterministic finite automaton** (NFA, 非確定性有限
自動機) allows several next states for one symbol, and optionally
`ε`-transitions (moves that consume no input). Formally,

```
δ : Q × (Σ ∪ {ε}) → P(Q).
```

An NFA accepts if *some* run ends in an accepting state. NFAs are not more
powerful: the **subset construction** converts an NFA with `n` states into a
DFA whose states are subsets of the NFA's states. The DFA can have up to
`2^n` states, and this blow-up is real: the language "the `n`-th symbol from
the end is `1`" has an `(n+1)`-state NFA but needs `2^n` DFA states.

**Minimization.** Two states are equivalent if they accept exactly the same
suffixes. Merging equivalent states gives the unique minimal DFA (up to
renaming). The number of states of the minimal DFA equals the number of
equivalence classes of the **Myhill–Nerode** relation: `x ≡_L y` iff for every
`z`, `xz ∈ L ⇔ yz ∈ L`.

### 1.6 Where DFAs live

* **Lexers**: recognize identifiers, numbers, keywords, and operators.
* **Protocols**: TCP states (`LISTEN`, `SYN-SENT`, `ESTABLISHED`, ...) are a
  finite-state machine.
* **Embedded control**: traffic lights, vending machines, elevators.
* **Regular expressions**: a theoretical regex is exactly a regular
  expression, compiled to an NFA/DFA. Warning: real regex engines with
  **backreferences** (for example `(a*)\1`) are *not* regular; they can
  recognize `{ww}`, which no DFA can.

The lesson of §1 is sharp: **finite memory buys speed and decidability, but
it cannot count without a bound.**

---

## 2. Grammars and the Chomsky hierarchy

### 2.1 Context-free grammars

A **grammar** describes a language *generatively*: it gives rules for
rewriting symbols until only terminals remain. A **context-free grammar**
(CFG, 上下文無關文法) is a 4-tuple

```
G = (V, Σ, R, S)
```

| Symbol | Meaning |
|---|---|
| `V` | finite set of **nonterminals** (variables), usually uppercase |
| `Σ` | finite set of **terminals** (the alphabet), disjoint from `V` |
| `R` | finite set of **productions** `A → α`, where `A ∈ V` and `α ∈ (V ∪ Σ)*` |
| `S` | the **start symbol**, `S ∈ V` |

"Context-free" means the left-hand side of every production is a *single*
nonterminal: `A` can be replaced by `α` regardless of what surrounds it. A
production with `α = ε` is an **ε-production** (empty production).

**Example: matching pairs.**

```
S → a S b | ε
```

This generates `ε`, `ab`, `aabb`, `aaabbb`, ... — the language
`{a^n b^n : n ≥ 0}`. The derivation

```
S ⇒ a S b ⇒ a a S b b ⇒ a a b b
```

is written `S ⇒* aabb`. Each `⇒` replaces one nonterminal using one
production. A **leftmost derivation** always replaces the leftmost
nonterminal; a **rightmost derivation** always replaces the rightmost one.

The **parse tree** records the same information as a tree:

```text
          S
        / | \
       a  S  b
        / | \
       a  S  b
          |
          ε
```

The **yield** of the tree (reading the leaves left to right) is `aabb`. A
string is in `L(G)` iff it is the yield of some parse tree rooted at `S`.

### 2.2 A grammar for arithmetic

A realistic grammar stratifies expressions by precedence:

```
E → E + T | T
T → T * F | F
F → ( E ) | id
```

`E` is an expression, `T` a term, `F` a factor. Because `*` is introduced
deeper in the tree, it binds tighter than `+`; because `E → E + T` recurses
on the left, `+` is left-associative. A leftmost derivation of
`id + id * id`:

```
E ⇒ E + T ⇒ T + T ⇒ F + T ⇒ id + T
  ⇒ id + T * F ⇒ id + F * F ⇒ id + id * F ⇒ id + id * id
```

Parse tree:

```text
              E
            / | \
           E  +  T
           |    / | \
           T   T  *  F
           |   |     |
           F   F    id
           |   |
          id  id
```

**Ambiguity.** The simpler grammar

```
E → E + E | E * E | ( E ) | id
```

also generates the same strings, but it gives `id + id * id` **two** parse
trees:

```text
     (id + id) * id              id + (id * id)

          E                           E
        / | \                       / | \
       E  *  E                     E  +  E
     / | \   |                     |    / | \
    E  +  E  id                   id   E  *  E
    |     |                            |     |
   id    id                           id    id
```

A grammar with two parse trees for one string is **ambiguous** (歧義). The
stratified grammar `E/T/F` removes the ambiguity by encoding precedence and
associativity in the shape of the tree. In practice, ambiguity is a bug:
different parsers may build different trees, and therefore different
programs, from the same source text.

**The dangling-else example.** This grammar is ambiguous:

```
S → if E then S
  | if E then S else S
  | other
```

For `if E1 then if E2 then S1 else S2`, the `else` can belong to either `if`.
Every mainstream language resolves it by the rule "an `else` matches the
nearest unmatched `if`", or by splitting statements into matched and
unmatched forms.

### 2.3 The Chomsky hierarchy

Noam Chomsky (1956, 1959) classified grammars by the shape of their
productions. The result is the **Chomsky hierarchy** (喬姆斯基／杭士基階層):

| Type | Name | Production form | Accepting machine | Language class |
|---|---|---|---|---|
| **3** | regular | `A → aB`, `A → a`, `A → ε` | DFA / NFA | regular |
| **2** | context-free | `A → γ` | PDA (nondeterministic) | context-free |
| **1** | context-sensitive | `αAβ → αγβ`, `γ ≠ ε` | linear-bounded automaton (LBA) | context-sensitive |
| **0** | unrestricted | `α → β`, `α` contains a nonterminal | Turing machine | recursively enumerable |

Here `A, B ∈ V`, `a ∈ Σ`, and `α, β, γ ∈ (V ∪ Σ)*`.

Some details that are easy to miss:

* **Type 3** may be **right-linear** (`A → aB`, `A → a`) or **left-linear**
  (`A → Ba`, `A → a`), but not a mixture of both. A mixed grammar can
  generate non-regular languages.
* **Type 2** is a subset of Type 1 in expressive power, but the strict
  production shape `αAβ → αγβ` forbids `A → ε`. The standard fix is to allow
  `S → ε` provided `S` never appears on a right-hand side. With that
  convention, every CFL is context-sensitive.
* **Type 1** is also called **noncontracting**: the right-hand side is never
  shorter than the left-hand side (except for the special `S → ε` rule).
  This is why an LBA — a Turing machine whose tape is limited to the input
  length — is the right machine model.
* **Type 0** is the most general: the left-hand side may be any string
  containing at least one nonterminal. These grammars generate exactly the
  recursively enumerable languages.

The **strict** chain is:

```
Type 3  ⊊  Type 2  ⊊  Type 1  ⊊  Type 0
regular    CF       CS        RE
```

Between regular and context-free sits the class of **deterministic
context-free languages** (DCFL), recognized by deterministic pushdown
automata. It is not one of Chomsky's four types, but it matters for parsing:
many programming-language grammars are deterministic. The refined chain is

```
regular ⊊ DCFL ⊊ CFL ⊊ CSL ⊊ recursive ⊊ RE
```

with these witnesses:

| Class | Example | Why it is not in the class below |
|---|---|---|
| regular | `{w : #1(w) is even}` | — |
| DCFL | `{a^n b^n}` | not regular (pumping lemma) |
| CFL | `{w w^R : w ∈ {a,b}*}` (even palindromes) | not deterministic |
| CSL | `{a^n b^n c^n}` | not context-free (pumping lemma) |
| recursive | TM descriptions that halt on ε within `2^n` steps (`n` = description length) | EXPTIME-complete, hence outside CSL ⊆ PSPACE |
| RE | `HALT` | not recursive (halting theorem) |
| not RE | `HALT`'s complement | no TM recognizes it |

The last row is outside the hierarchy altogether: there are languages that
no Turing machine can even list.

### 2.4 What context-free grammars cannot do

**Pumping lemma for CFLs.** If `L` is context-free, there is a number `p`
such that every `w ∈ L` with `|w| ≥ p` can be written

```
w = u v x y z,     |vxy| ≤ p,     |vy| ≥ 1,
```

and `u v^i x y^i z ∈ L` for every `i ≥ 0`. The middle three pieces are the
"pumpable" part; the two pieces `v` and `y` are pumped together.

**Example: `{a^n b^n c^n}` is not context-free.** Suppose it is, with pumping
length `p`, and take `w = a^p b^p c^p`. Since `|vxy| ≤ p`, the window `vxy`
can touch at most two of the three blocks (crossing all three blocks would
require at least `p + 2` symbols: one `a`, all `p` `b`s, and one `c`).
Pumping therefore changes the count in at most two blocks while leaving the
third unchanged, so the three counts cannot stay equal. Contradiction.

A second proof uses **closure properties**. The languages

```
L1 = {a^i b^j c^k : i = j}        L2 = {a^i b^j c^k : j = k}
```

are context-free (each is basically `a^n b^n` followed by `c*`, or `a*`
followed by `b^n c^n`). Their intersection is `{a^n b^n c^n}`, which is not
context-free. Hence CFLs are **not closed under intersection**. Since CFLs
are closed under union, they cannot be closed under complement either:
if they were, `L1 ∩ L2 = complement(complement(L1) ∪ complement(L2))` would
be context-free.

**Closure and decidability at a glance.**

| Property | Regular | CFL | CSL | Recursive | RE |
|---|---|---|---|---|---|
| union | ✓ | ✓ | ✓ | ✓ | ✓ |
| intersection | ✓ | ✗ | ✓ | ✓ | ✓ |
| complement | ✓ | ✗ | ✓ | ✓ | ✗ |
| concatenation | ✓ | ✓ | ✓ | ✓ | ✓ |
| Kleene star | ✓ | ✓ | ✓ | ✓ | ✓ |
| membership decidable | ✓ | ✓ | ✓ | ✓ | semi-decidable |
| emptiness decidable | ✓ | ✓ | ✗ | ✗ | ✗ |
| equivalence decidable | ✓ | ✗ | ✗ | ✗ | ✗ |

Two entries deserve comment:

* **Context-sensitive languages are closed under complement.** This is the
  Immerman–Szelepcsényi theorem (1988), a famous result: nondeterministic
  space classes are closed under complement.
* **Emptiness of a context-sensitive grammar is undecidable.** Membership is
  decidable (in fact PSPACE-complete), but deciding whether the grammar
  generates *any* string is not. Do not confuse the two.

### 2.5 Parsing in practice

A parser turns a string into a parse tree (or reports a syntax error). The
classical algorithms:

* **CYK** (Cocke–Younger–Kasami): requires the grammar in **Chomsky normal
  form** (CNF, `A → BC`, `A → a`, or `S → ε`). It fills a table `T[i][j]`
  containing the nonterminals that derive `w[i:j]`, splitting at every `k`
  with `i < k < j`. Time `O(n^3)`, space `O(n^2)`. It is simple and general
  but slow for long inputs.
* **Earley**: general CFG, `O(n^3)` worst case, `O(n^2)` for unambiguous
  grammars, and often linear in practice.
* **LL(k)**: top-down, left-to-right, predicts the next production from the
  next `k` symbols. Recursive-descent parsers are usually LL(1).
* **LR(k)**: bottom-up, handles a larger class; `yacc`/`bison` generate
  LR(1) or LALR(1) parsers. Many production parsers use LR tools; many others
  are hand-written recursive-descent parsers.

**Left recursion** must be removed for LL parsers. The rule

```
A → A α | β          becomes          A  → β A'
                                       A' → α A' | ε
```

and the transformed grammar accepts the same language.

**Regex vs CFG.** A regular expression cannot match unbounded nesting:
`(`, `(())`, `((()))`, ... is not regular. A CFG can:

```
S → ( S ) S | ε
```

That is why programming languages need a grammar, not just a regex. But even
a CFG cannot enforce every rule: "a variable must be declared before it is
used" depends on a symbol table and the surrounding context. Such checks are
done in **semantic analysis**, often with attribute grammars or a
context-sensitive formalism. The practical pipeline is:

```
source text → lexer (DFA) → parser (CFG) → semantic analysis → ...
```

**A tiny derivation engine.** The following program searches for a leftmost
derivation of a target string. It expands only the leftmost nonterminal, so
the path it prints is a genuine leftmost derivation:

```python
from collections import deque

GRAMMAR = {"S": ["aSb", ""]}          # S → aSb | ε


def leftmost_derivation(grammar, start, target):
    queue = deque([(start, [start])])
    seen = {start}
    while queue:
        form, path = queue.popleft()
        if form == target:
            return path
        for i, ch in enumerate(form):
            if ch in grammar:
                for rhs in grammar[ch]:
                    new = form[:i] + rhs + form[i + 1:]
                    if len(new) <= len(target) + 1 and new not in seen:
                        seen.add(new)
                        queue.append((new, path + [new]))
                break              # only the leftmost nonterminal
    return None


for n in range(4):
    target = "a" * n + "b" * n
    path = leftmost_derivation(GRAMMAR, "S", target)
    print(target or "ε", "=>", " => ".join(p or "ε" for p in path))
print("aab =>", leftmost_derivation(GRAMMAR, "S", "aab"))
```

```text
ε => S => ε
ab => S => aSb => ab
aabb => S => aSb => aaSbb => aabb
aaabbb => S => aSb => aaSbb => aaaSbbb => aaabbb
aab => None
```

The last line is the important one: `aab` has no derivation, so the search
returns `None`. A parser is a decision procedure for `w ∈ L(G)`; a
generator enumerates `L(G)`. The two directions are not the same problem.

---

## 3. Lambda calculus: functions as computation

### 3.1 Syntax

The **λ-calculus** (λ 演算, lambda calculus) was introduced by Alonzo Church
in the 1930s as a formal system for functions. Its entire syntax is three
rules:

```
e ::= x            variable
    | λx. e        abstraction (a function of x)
    | e e          application (apply the first term to the second)
```

Conventions:

* Application is **left-associative**: `f x y` means `(f x) y`.
* Abstraction extends as far right as possible: `λx. x y` means
  `λx. (x y)`.
* `λx. λy. e` is often written `λx y. e`.

There are no numbers, booleans, `if`, loops, or assignment in the raw
calculus. Everything is a function. The surprise of the next subsections is
that this is enough to encode all of computation.

### 3.2 Free and bound variables; closed terms

In `λx. e`, the variable `x` is **bound** inside `e`. A variable that is not
bound by an enclosing abstraction is **free**. The set of free variables is
defined recursively:

```
FV(x)       = {x}
FV(λx. e)   = FV(e) \ {x}
FV(e1 e2)   = FV(e1) ∪ FV(e2)
```

A term `e` is **closed** iff `FV(e) = ∅`. Closed terms are also called
**combinators** (組合子). They are the "closed packages" of the λ-calculus:
no external environment is needed to give meaning to their variables.

| Term | Free variables | Closed? |
|---|---|---|
| `x` | `{x}` | no |
| `λx. x` | `∅` | yes (identity) |
| `λx. y` | `{y}` | no |
| `λx. λy. x` | `∅` | yes (`K`) |
| `λx. x x` | `∅` | yes |
| `Y` | `∅` | yes |
| `λx. y x` | `{y}` | no |

The closed term `λx. x x` is the self-application that powers the Y
combinator. A closed term is a complete program: evaluating it starts with an
empty environment.

**A tiny complete basis.** The combinators

```
I = λx. x
K = λx. λy. x
S = λx. λy. λz. x z (y z)
```

are closed, and every λ-term can be translated into a term built only from
`S`, `K`, and `I` (bracket abstraction). For example, `S K K` behaves like
`I`:

```
S K K x → K x (K x) → x.
```

So computation can be reduced to a handful of closed rewriting rules. This
is the theoretical ancestor of **combinatory logic** and of point-free
functional programming.

### 3.3 Reduction: α, β, and η

**α-conversion (renaming).** Bound variables are placeholders:

```
λx. x  =α  λy. y.
```

Renaming must also respect scope. `λx. λy. x` is not the same as
`λx. λx. x`; the inner binder shadows the outer one.

**β-reduction (application).** The central rule:

```
(λx. M) N  →β  M[x := N]
```

`M[x := N]` is **substitution**: replace every *free* occurrence of `x` in
`M` by `N`. Substitution must be **capture-avoiding**. For example,

```
(λx. λy. x) y  →  λy. y        WRONG: the free y was captured
(λx. λy. x) y  →  λy'. y       RIGHT: rename the bound y first
```

This is exactly why real implementations rename variables or use **de Bruijn
indices** (HW6's interpreter supports both). De Bruijn indices replace names
by distances to their binders, so α-conversion disappears and substitution
is just index arithmetic.

**η-conversion (extensionality).** If `x` does not occur free in `M`,

```
λx. M x  →η  M.
```

Both sides are the same function: applied to any argument, they return the
same result. η is useful for simplifying `λf. λx. f x` to `λf. f`.

**Reduction strategies.** A **redex** is a term of the form `(λx. M) N`.
Different strategies choose different redexes:

* **Normal order**: reduce the leftmost-outermost redex first. This is the
  strategy that finds a normal form whenever one exists.
* **Call-by-name**: pass the argument unevaluated; evaluate it every time it
  is used.
* **Call-by-value**: evaluate the argument to a value before substituting.
  This is what Python, Java, and most strict languages do.

The strategies differ on terms that contain a divergent subterm:

```
Ω = (λx. x x) (λx. x x)        Ω → Ω → Ω → ...
```

`Ω` has no normal form. Now consider

```
(λx. λy. y) Ω.
```

Normal order ignores the unused argument and returns `λy. y`. Call-by-value
evaluates `Ω` first and diverges. A language's evaluation strategy is
therefore observable: it can turn a terminating program into a non-terminating
one.

**The Church–Rosser theorem (confluence).** If `M →* N1` and `M →* N2`, there
is a term `N3` with `N1 →* N3` and `N2 →* N3`. Consequently, if a term has a
normal form, that normal form is unique up to α-conversion. Reduction order
affects *whether* and *how fast* you reach it, not *what* it is.

### 3.4 Closures in programming languages (the other "closed package")

The word **closure** (閉包 / 封閉包) has several meanings. In programming
languages it means a function together with the **environment** in which it
was created. The function "closes over" the free variables, capturing their
values so they remain available after the enclosing scope has returned.

```python
def make_adder(n):
    return lambda x: x + n

add5 = make_adder(5)
print(add5(3))        # 8
print(add5(10))       # 15
```

`add5` is a closure: its code is `λx. x + n`, and its environment binds
`n = 5`. Without closures, the function would have to receive `n` on every
call. Closures are what make **currying** and **partial application** work:

```python
add = lambda n: lambda x: x + n
add5 = add(5)         # a closure carrying n = 5
```

In λ-calculus terms, a closure is a pair

```
(λx. M, ρ)
```

where `ρ` is an environment mapping the free variables of `λx. M` to values
(or to other closures). Environment-based evaluators — the SECD machine and
the Krivine machine are the classics — use exactly this pair. A
substitution-based evaluator, like the one in §3.7, does not need closures;
it copies terms instead. Both implement the same calculus.

**Four things called "closure".** The word is overloaded; keep them apart:

| Term | Meaning | Where it appears |
|---|---|---|
| **closed term** | a λ-term with no free variables | λ-calculus (§3.2) |
| **closure** | code + captured lexical environment | programming languages (§3.4) |
| **ε-closure** | states reachable by ε-transitions | NFA construction (§1.5) |
| **closure property** | a class closed under an operation | formal languages (§2.4) |

A closure in the programming sense is not the same as a closed term. A
closed term needs no environment; a closure *is* a code pointer plus an
environment. The shared intuition is "self-contained package", but the
technical objects are different.

### 3.5 Church encodings

Church showed that data can be encoded as functions. The encoding is a
party trick with a serious point: **functions are universal data.**

| Concept | λ-term | Intuition |
|---|---|---|
| `TRUE` | `λt. λf. t` | select the first of two things |
| `FALSE` | `λt. λf. f` | select the second |
| `IF` | `λp. λa. λb. p a b` | apply the boolean to both branches |
| `AND` | `λp. λq. p q p` | if `p` then `q` else `p` |
| `OR` | `λp. λq. p p q` | if `p` then `p` else `q` |
| `NOT` | `λp. p FALSE TRUE` | swap the branches |
| `0` | `λf. λx. x` | apply `f` zero times |
| `1` | `λf. λx. f x` | apply `f` once |
| `n` | `λf. λx. f (f ... (f x))` | apply `f` `n` times |
| `SUCC` | `λn. λf. λx. f (n f x)` | one more application |
| `ADD` | `λm. λn. λf. λx. m f (n f x)` | compose the applications |
| `MUL` | `λm. λn. λf. m (n f)` | `m` copies of `n` copies |
| `POW` | `λm. λn. n m` | `n`-fold composition of `m` |
| `ISZERO` | `λn. n (λx. FALSE) TRUE` | is the count zero? |
| `PRED` | `λn. λf. λx. n (λg. λh. h (g f)) (λu. x) (λu. u)` | one less (the hard one) |
| `PAIR` | `λa. λb. λf. f a b` | a pair is a two-argument selector |
| `FST` | `λp. p TRUE` | first projection |
| `SND` | `λp. p FALSE` | second projection |

A worked reduction:

```
ADD 2 3
= (λm. λn. λf. λx. m f (n f x)) 2 3
→ λf. λx. 2 f (3 f x)
→ λf. λx. f (f (f (f (f x))))       = 5
```

`PRED` is famously awkward because Church numerals are "iterate `n` times",
and subtracting one requires iterating over *pairs* of values. Its exact
encoding is not important for understanding; what matters is that it exists,
so the entire recursive function theory is expressible.

### 3.6 Recursion without names: the Y combinator

A λ-term has no name, so it cannot refer to itself:

```
FACT = λn. if n = 0 then 1 else n * FACT (n - 1)     -- illegal: FACT is not defined
```

The **Y combinator** (Y 組合子) solves this. Define

```
Y = λf. (λx. f (x x)) (λx. f (x x))
```

Then, for any term `g`,

```
Y g → (λx. g (x x)) (λx. g (x x))
    → g ((λx. g (x x)) (λx. g (x x)))
    = g (Y g).
```

So `Y g` is a **fixed point** of `g`: applying `g` to it gives the same
thing back (up to β-equivalence). If `g` is written as a function that
expects "itself" as its first argument, then `Y g` *is* the recursive
function:

```
FACT = Y (λf. λn. IF (ISZERO n) 1 (MUL n (f (PRED n))))
```

Evaluation of `FACT 3`:

```
FACT 3
→ (λf. λn. IF (ISZERO n) 1 (MUL n (f (PRED n)))) (Y ...) 3
→ IF (ISZERO 3) 1 (MUL 3 ((Y ...) (PRED 3)))
→ MUL 3 ((Y ...) 2)
→ MUL 3 (MUL 2 ((Y ...) 1))
→ MUL 3 (MUL 2 (MUL 1 ((Y ...) 0)))
→ MUL 3 (MUL 2 (MUL 1 1))
→ 6
```

The recursion is created by the self-application `x x` inside `Y`. `Y`
itself is not recursive; it is a closed term that duplicates a function and
feeds it back to itself. This is **controlled self-reference**, and its
uncontrolled cousin is `Ω`:

```
Ω = (λx. x x) (λx. x x)
```

`Ω` keeps self-applying forever. `Y` puts the self-application under `f`, so
`f` can choose to stop (when `n = 0`) or to recurse (when `n > 0`).

**Why Y is not typable in simply typed λ-calculus.** In `λx. x x`, the
variable `x` is applied to itself, so it would need a type `τ` that is also
a function type `τ → σ`. No finite simple type satisfies `τ = τ → σ`. This
is not a bug: it is exactly why the simply typed λ-calculus is **strongly
normalizing** (every term terminates) and therefore not Turing-complete.
Adding a fixed-point operator or recursive types gives the power back, at
the cost of losing the guarantee that every program terminates.

**Call-by-value and the Z combinator.** In a call-by-value language the
classic `Y` evaluates `g (Y g)` eagerly and can diverge before reaching the
base case. The standard fix is the **Z combinator**, which delays the
recursive call with an extra `λv`:

```
Z = λf. (λx. f (λv. x x v)) (λx. f (λv. x x v))
```

In Python, where function arguments are evaluated eagerly, the same idea
looks like this (this is the Z combinator, written in Python):

```python
Z = lambda f: (lambda x: f(lambda v: x(x)(v)))(lambda x: f(lambda v: x(x)(v)))
fact = Z(lambda f: lambda n: 1 if n == 0 else n * f(n - 1))
print(fact(5))     # 120
```

The `lambda v: ...` is the delay. Without it, Python would try to evaluate
`x(x)` immediately and hit the recursion limit.

### 3.7 A tiny interpreter

The following interpreter implements the core of §3.3: terms are tuples,
substitution is capture-avoiding, and `step` reduces the leftmost-outermost
redex. It is small enough to read in one sitting, and it really runs the
Church encodings.

```python
# terms: ('var', name) | ('lam', name, body) | ('app', f, arg)
def V(x): return ("var", x)
def L(x, b): return ("lam", x, b)
def A(f, a): return ("app", f, a)


def fv(t):
    if t[0] == "var": return {t[1]}
    if t[0] == "lam": return fv(t[2]) - {t[1]}
    return fv(t[1]) | fv(t[2])


def fresh(x, used):
    while x in used:
        x += "'"
    return x


def subst(t, x, s):                       # capture-avoiding t[x := s]
    if t[0] == "var":
        return s if t[1] == x else t
    if t[0] == "lam":
        y, body = t[1], t[2]
        if y == x:
            return t
        if y in fv(s):                    # rename the bound variable
            z = fresh(y, fv(s) | fv(body) | {x})
            return L(z, subst(subst(body, y, V(z)), x, s))
        return L(y, subst(body, x, s))
    return A(subst(t[1], x, s), subst(t[2], x, s))


def step(t):                              # one normal-order beta step
    if t[0] == "app":
        f, a = t[1], t[2]
        if f[0] == "lam":
            return subst(f[2], f[1], a)
        nf = step(f)
        if nf is not None:
            return A(nf, a)
        na = step(a)
        if na is not None:
            return A(f, na)
        return None
    if t[0] == "lam":
        nb = step(t[2])
        return L(t[1], nb) if nb is not None else None
    return None


def normalize(t, limit=100_000):
    for i in range(limit):
        nxt = step(t)
        if nxt is None:
            return t, i
        t = nxt
    raise RuntimeError("step limit exceeded")


def show(t, prec=0):
    if t[0] == "var": return t[1]
    if t[0] == "lam":
        s = "λ" + t[1] + "." + show(t[2])
        return "(" + s + ")" if prec else s
    s = show(t[1], 1) + " " + show(t[2], 2)
    return "(" + s + ")" if prec > 1 else s


def church(n):
    f, x = V("f"), V("x")
    body = x
    for _ in range(n):
        body = A(f, body)
    return L("f", L("x", body))


def to_int(t):
    if t[0] != "lam" or t[2][0] != "lam":
        return None
    f, x, body, n = t[1], t[2][1], t[2][2], 0
    while body[0] == "app" and body[1] == V(f):
        n, body = n + 1, body[2]
    return n if body == V(x) else None
```

Now the encodings and a demo:

```python
TRUE   = L("t", L("f", V("t")))
FALSE  = L("t", L("f", V("f")))
IF     = L("p", L("a", L("b", A(A(V("p"), V("a")), V("b")))))
ISZERO = L("n", A(A(V("n"), L("x", FALSE)), TRUE))
MUL    = L("m", L("n", L("f", L("x", A(A(V("m"), A(V("n"), V("f"))), V("x"))))))
PRED   = L("n", L("f", L("x",
    A(
        A(
            A(V("n"), L("g", L("h", A(V("h"), A(V("g"), V("f")))))),
            L("u", V("x")),
        ),
        L("u", V("u")),
    )
)))
Y      = L("f", A(L("x", A(V("f"), A(V("x"), V("x")))),
                  L("x", A(V("f"), A(V("x"), V("x"))))))
FACT   = A(Y, L("f", L("n",
    A(A(A(IF, A(ISZERO, V("n"))), church(1)),
      A(A(MUL, V("n")), A(V("f"), A(PRED, V("n"))))))))

# Capture avoidance: (λx. λy. x) y  ->  λy'. y
t = A(L("x", L("y", V("x"))), V("y"))
print(show(normalize(t)[0]))              # λy'.y

# PRED 3 = 2
print(show(normalize(A(PRED, church(3)))[0]))

# FACT 0..4
for n in range(5):
    result, steps = normalize(A(FACT, church(n)))
    print(f"FACT {n} = {to_int(result)}  ({steps} beta steps)")
```

Output:

```text
λy'.y
λf.λx.f (f x)
FACT 0 = 1  (12 beta steps)
FACT 1 = 1  (37 beta steps)
FACT 2 = 2  (145 beta steps)
FACT 3 = 6  (704 beta steps)
FACT 4 = 24  (4109 beta steps)
```

The step counts grow quickly — that is the cost of unary Church numerals and
of the substitution-based evaluator. A real implementation uses de Bruijn
indices and/or an environment machine. HW6's interpreter uses de Bruijn
indices, and adds a call-by-value strategy, step traces, and a REPL; see
[`../HW6/README.md`](../HW6/README.md).

### 3.8 Typed vs untyped

The **untyped** λ-calculus is Turing-complete: it can express every
computable function, including `Ω`. The **simply typed** λ-calculus assigns
each term a type and rejects self-application; every well-typed term
terminates. This is the theoretical basis of proof assistants such as Coq,
Agda, and Lean: a proof checker must be guaranteed to terminate, otherwise
it could loop instead of certifying a proof.

The price of types is expressiveness. To recover general recursion, a typed
language adds a fixed-point operator, recursive types, or a general
`let rec`. Haskell's `fix` is a direct relative of `Y`; Python's named
recursive functions achieve the same effect with a function name. The
untyped calculus remains the cleanest setting for studying computation
itself.

---

## 4. Turing machines and the limits of computation

### 4.1 Formal definition

A **Turing machine** (TM, 圖靈機) is a 7-tuple

```
M = (Q, Γ, Σ, δ, q0, q_accept, q_reject)
```

| Symbol | Meaning |
|---|---|
| `Q` | finite set of states |
| `Γ` | finite **tape alphabet** |
| `Σ` | **input alphabet**, `Σ ⊆ Γ \ {⊔}` |
| `⊔` | the **blank symbol**, `⊔ ∈ Γ` but `⊔ ∉ Σ` |
| `δ` | transition function, `δ : Q × Γ → Q × Γ × {L, R}` |
| `q0` | start state |
| `q_accept`, `q_reject` | halting states, distinct |

The machine has:

* an **infinite tape** divided into cells, each holding one symbol from `Γ`;
* a **head** that reads and writes one cell and moves one cell left or right;
* a **finite control** (the current state).

The tape is the machine's memory. It is unbounded in both directions, so the
machine can store as much as it needs, but it can access a cell only by
moving the head there. That is slower than random access, but not less
powerful: a TM can simulate an array by walking back and forth.

Some books use a 6-tuple and omit `q_reject`; a missing transition or a
separate halting convention does the same job. Some allow `δ` to be partial.
These choices do not change the class of computable functions.

**Configurations.** A configuration is written `u q v`, where `u` is the
tape to the left of the head, `v` is the tape from the head rightward, and
`q` is the current state. The initial configuration on input `w` is `q0 w`.
The machine accepts if it reaches `u q_accept v` and rejects if it reaches
`u q_reject v`. It may also run forever, which is the third possible
outcome.

### 4.2 Worked example: binary increment

The following TM adds 1 to a binary number. The input is written on the tape
with the least significant bit on the right; the head starts at the leftmost
symbol.

| State | Read | Write | Move | Next | Meaning |
|---|---|---|---|---|---|
| `scan` | `0` | `0` | R | `scan` | walk to the end |
| `scan` | `1` | `1` | R | `scan` | walk to the end |
| `scan` | `⊔` | `⊔` | L | `carry` | found the end |
| `carry` | `1` | `0` | L | `carry` | `1 + 1 = 0`, carry left |
| `carry` | `0` | `1` | R | `accept` | `0 + 1 = 1`, done |
| `carry` | `⊔` | `1` | R | `accept` | all ones; write a new leading 1 |

Example: `1011` (eleven) becomes `1100` (twelve):

```text
step 0   scan    [1] 0 1 1 ⊔
step 4   scan     1 0 1 1 [⊔]
step 5   carry    1 0 1 [1] ⊔
step 6   carry    1 0 [1] 0 ⊔
step 7   carry    1 [0] 0 0 ⊔
step 8   accept   1 1 [0] 0 ⊔
```

The brackets mark the head. The machine scans to the right end, then walks
left through the trailing `1`s, turning each into `0`. At the first `0` it
writes `1` and stops. If the number is all `1`s, it writes a new `1` on the
blank cell to the left.

A Python simulator:

```python
class TM:
    def __init__(self, delta, start, accept, reject, blank="⊔"):
        self.delta = delta
        self.start = start
        self.accept = accept
        self.reject = reject
        self.blank = blank

    def run(self, word, max_steps=10000):
        tape = {i: ch for i, ch in enumerate(word)}
        head, state = 0, self.start
        for step in range(max_steps):
            if state == self.accept:
                return True, step, self.show(tape, head)
            symbol = tape.get(head, self.blank)
            if state == self.reject or (state, symbol) not in self.delta:
                return False, step, self.show(tape, head)
            write, move, state = self.delta[(state, symbol)]
            tape[head] = write
            head += 1 if move == "R" else -1
        return None, max_steps, self.show(tape, head)   # did not halt

    @staticmethod
    def show(tape, head):
        lo, hi = min([0, *tape]), max([0, *tape])
        cells = [tape.get(i, "⊔") for i in range(lo, hi + 2)]
        return "".join(cells) + "\n" + " " * (head - lo) + "^"


INC = TM(
    delta={
        ("scan", "0"): ("0", "R", "scan"),
        ("scan", "1"): ("1", "R", "scan"),
        ("scan", "⊔"): ("⊔", "L", "carry"),
        ("carry", "1"): ("0", "L", "carry"),
        ("carry", "0"): ("1", "R", "accept"),
        ("carry", "⊔"): ("1", "R", "accept"),
    },
    start="scan",
    accept="accept",
    reject="reject",
)

for word in ["1011", "111", "0", ""]:
    ok, steps, tape = INC.run(word)
    print(f"{word or 'ε':>6} -> {tape.splitlines()[0].strip('⊔')}  "
          f"(accepted={ok}, steps={steps})")
```

```text
  1011 -> 1100  (accepted=True, steps=8)
   111 -> 1000  (accepted=True, steps=8)
     0 -> 1  (accepted=True, steps=3)
     ε -> 1  (accepted=True, steps=2)
```

The simulator represents the infinite tape as a dictionary, so cells are
created only when written. `max_steps` is a safety valve: a real TM has no
such limit, and `run` returns `None` if it hits the limit.

### 4.3 Variants and robustness

Many apparently stronger machines turn out to be equivalent:

| Variant | Change | Still equivalent? |
|---|---|---|
| multi-tape TM | several tapes, independent heads | yes (simulate on one tape; `O(t^2)` slowdown) |
| nondeterministic TM | several possible moves per configuration | yes (search the computation tree) |
| two-way infinite tape | tape extends left and right | yes (fold it onto a one-way tape) |
| larger alphabet | more symbols per cell | yes (encode symbols in binary) |
| RAM machine | random-access memory, arithmetic | yes (simulate memory with the tape) |
| λ-calculus | functions and substitution | yes (Church–Turing) |
| cellular automaton | local update rules on a grid | yes (Rule 110, Game of Life) |

This robustness is the empirical heart of the Church–Turing thesis: every
reasonable attempt to formalize "algorithm" lands on the same class.

**The universal Turing machine.** A Turing machine can be encoded as a finite
string `⟨M⟩`, because `Q`, `Γ`, and `δ` are finite. There is therefore a
**universal Turing machine** `U` that takes a pair `(⟨M⟩, w)` and simulates
`M` on `w`:

```
U(⟨M⟩, w) = M(w).
```

This is the stored-program idea: one machine can run any program. It also
makes self-reference possible, which is the engine of the halting proof.
`U` is still an ordinary TM; there is no "super-machine" needed to simulate
other machines.

### 4.4 Recognizers vs deciders

Two different success criteria:

* A **recognizer** for `L` accepts every `w ∈ L` and may loop forever on
  `w ∉ L`. `L` is **recursively enumerable** (RE, 遞迴可列舉).
* A **decider** for `L` halts on every input: it accepts `w ∈ L` and rejects
  `w ∉ L`. `L` is **recursive** or **decidable** (可判定).

Every decidable language is RE (a decider is a recognizer that always
halts), but not conversely. The halting problem is the standard witness:
it is RE but not decidable.

A useful theorem: **if both `L` and its complement are RE, then `L` is
decidable.** Run the two recognizers in parallel, one step at a time. Every
string belongs to exactly one of them, so one of the two must eventually
accept; stop and answer accordingly. This is called **dovetailing**.

### 4.5 The halting problem

The assignment calls this the *"downtime"* question: given a program and an
input, does the program eventually stop? Formally,

```
HALT = { (⟨M⟩, w) : M halts on input w }.
```

**Theorem (Turing, 1936).** `HALT` is undecidable.

**Proof.** Suppose, for contradiction, that some TM `H` decides `HALT`:

```
H(⟨M⟩, w) = accept   if M halts on w
H(⟨M⟩, w) = reject   if M loops forever on w
```

Build a new machine `D` (the diagonal machine) that takes a machine
description `⟨M⟩` and does the opposite:

```python
# H is the hypothetical decider for HALT (it cannot actually exist).
def D(M):
    if H(M, M):
        while True:          # H says M(M) halts: loop forever
            pass
    else:
        return               # H says M(M) loops: halt immediately
```

Now ask what `D` does on its own description:

```
D(⟨D⟩) halts
  ⇔ H(⟨D⟩, ⟨D⟩) = reject        (by the definition of D)
  ⇔ D(⟨D⟩) does not halt        (by the definition of H)
```

The two lines contradict each other. Therefore `H` cannot exist, and `HALT`
is undecidable. ∎

The proof is **Cantor's diagonal argument** in computational clothing:

```text
          M0      M1      M2      M3    ...
  M0      halt    loop    halt    halt
  M1      loop    loop    halt    loop
  M2      halt    halt    loop    halt
  M3      loop    halt    halt    loop
  ...
   D      loop    halt    halt    halt   ← opposite of every diagonal entry
```

If the rows were a complete list of all machines, `D` would have to appear
somewhere. But `D` differs from row `i` at input `M_i` — the diagonal — so it
is not in the list. Contradiction. The list cannot be complete.

**What exactly is undecidable?**

* `HALT` is **RE**: a universal TM can simulate `M` on `w` and accept if it
  halts. It cannot reject the looping cases, because it never finishes
  simulating them.
* The complement of `HALT` is **not RE**. There is no machine that accepts
  exactly the pairs that loop forever.
* The **diagonal language** `L_d = {⟨M⟩ : M does not accept ⟨M⟩}` is not RE.
  It is the cleanest "outside the hierarchy" example.
* `HALT` is not "hard because it takes a long time". It is outside the class
  of decidable problems entirely: no algorithm, with any amount of time,
  decides it for all inputs.

**Rice's theorem.** Every **nontrivial semantic property** of programs is
undecidable. A property is semantic if it depends on the function the
program computes, not on its source text; it is nontrivial if some programs
have it and some do not. Examples:

* "Does this program ever output `42`?"
* "Is this program equivalent to that one?"
* "Does this program compute a constant function?"
* "Is the domain of this program finite?"

Rice's theorem says all of these are undecidable. Syntactic properties ("does
the source contain the word `while`?") are usually decidable; semantic ones
are not. This is why no perfect static analyzer exists: every real analyzer
must be **sound but incomplete** (it may miss bugs) or **complete but
unsound** (it may report false alarms), or it must restrict the language it
analyzes.

**The busy beaver function.** Let `BB(n)` be the maximum number of steps a
halting `n`-state binary TM can make on a blank tape. `BB` is well-defined,
but it is **uncomputable**: if you could compute `BB(n)`, you could decide
whether an `n`-state machine halts on a blank tape by simulating it for
`BB(n)` steps. Its growth is spectacular. `BB(5) = 47,176,870` was only
settled in 2024; `BB(6)` is already beyond current methods. Uncomputability
is not a far-away theoretical curiosity: the first few values already
exhaust our tools.

**Why finite machines escape.** A DFA always halts after `|w|` steps; a PDA
has decidable membership; an LBA has a finite (though input-dependent)
configuration space. Undecidability needs **unbounded memory**, because that
is what allows a computation to run for an unbounded number of steps without
repeating a configuration.

### 4.6 The Church–Turing thesis

**Statement.** Every function that is **effectively computable** — computable
by a human following a finite, deterministic set of rules with unlimited
paper and time — is computable by a Turing machine. Equivalently, all
reasonable models of computation define the same class of computable
functions.

This is a **thesis**, not a theorem. "Effectively computable" is an informal
notion; it has no formal definition to prove equivalence against. The thesis
is a scientific hypothesis about the meaning of "algorithm", supported by
evidence:

* **Independent formalizations coincide.** Church's λ-definable functions
  (1936), Turing's machines (1936), Gödel–Herbrand–Kleene recursive
  functions, Post's systems, Curry's combinatory logic, Markov algorithms,
  register machines, and cellular automata all define the same class.
* **No counterexample in ninety years.** Nobody has exhibited a concrete,
  physically realizable procedure that computes a function no TM can
  compute.
* **Robustness.** The variants in §4.3 all simulate each other. Adding
  tapes, nondeterminism, or a bigger alphabet changes speed, not power.

**How it could fail.** A single counterexample would refute it: a physical
process or a finite procedure that computes a non-TM-computable function.
Proposals exist under the name **hypercomputation** — oracle machines,
infinite-time Turing machines, analog computers over the real numbers,
quantum gravity models — but none has been physically realized or generally
accepted. They are mathematical models, not evidence against the thesis.

**Variants of the thesis.**

| Name | Claim | Status |
|---|---|---|
| Church–Turing thesis | effectively computable = TM-computable | the standard thesis |
| Physical Church–Turing thesis | every physically realizable computation is TM-computable | a claim about physics; open |
| Strong Church–Turing thesis (Cobham–Edmonds) | TM with polynomial overhead captures *feasible* computation | a complexity hypothesis; debated |

The **strong** thesis is about efficiency, not just computability. Quantum
computers do not violate the ordinary thesis: a quantum computer computes
functions that a TM can also compute (given enough time). They may violate
the strong thesis if they solve, in polynomial time, problems that no
classical polynomial-time machine can — the factoring problem is the famous
candidate. That is a statement about complexity, not about the boundary of
the computable.

**Consequences.**

* One universal model suffices. A new programming language, CPU, or
  calculator does not add computational power; it adds convenience, speed,
  or memory.
* Undecidability is **model-independent**. If `HALT` is undecidable for TMs,
  it is undecidable for Python, Java, λ-calculus, and every other
  Turing-complete system. A proof for one model transfers to all.
* "Turing-complete" is a warning label. Any system with unbounded memory,
  conditionals, and loops inherits the halting problem. This includes
  interpreters, macro systems, and even some configuration languages.
* Hardware improvements change **how fast** we compute, not **what** is
  computable.

**History.** In 1928 David Hilbert posed the *Entscheidungsproblem*: is there
an algorithm that decides whether a first-order logical formula is valid? In
1936 Church (using λ-definability) and Turing (using machines) independently
proved that no such algorithm exists. Turing's paper also introduced the
universal machine and proved the halting problem undecidable. The thesis is
named after both of them because their formalisms turned out to be
equivalent.

### 4.7 Complexity after computability

Computability asks *whether* a problem can be decided at all. Complexity
asks *how much time or space* a decision procedure needs. The two walls are
different:

* **Undecidable**: no algorithm, no matter how much time.
* **Intractable**: an algorithm exists, but no known efficient one.

A useful bridge is **bounded halting**:

```
HALT_T = { (⟨M⟩, w, t) : M halts on w within t steps }.
```

`HALT_T` is **decidable**: simulate `M` for `t` steps. The bound `t` is
written in binary, so the simulation is `O(t)` — exponential in the length of
the input — but it always gives an answer. This is why timeouts, bounded model
checking, and "run it for 10 seconds" work: they decide a bounded version of
an unbounded problem.

The standard complexity classes:

```
P ⊆ NP ⊆ PSPACE ⊆ EXPTIME
```

`P` is deterministic polynomial time; `NP` is nondeterministic polynomial
time; `PSPACE` is polynomial space; `EXPTIME` is exponential time.
`P ⊊ EXPTIME` is known (time hierarchy theorem); whether `P = NP` is the most
famous open problem in computer science. `SAT`, `3-SAT`, Hamiltonian cycle,
and the decision version of TSP are NP-complete: they are decidable, but no
polynomial-time algorithm is known, and finding one would prove `P = NP`.

The two walls interact in practice. A compiler can parse a program (CFG,
decidable), but it cannot decide all semantic properties of the program
(Rice, undecidable). A static analyzer therefore approximates: it checks a
decidable property that implies the one you care about, or it restricts the
language (for example, to finite-state protocols or terminating functions).

**A subtlety about real machines.** A physical computer has finite memory, so
its set of configurations is finite. In principle, you could decide whether a
deterministic program halts on a fixed input by simulating it until it repeats
a configuration. In practice the state space is astronomical (far more than
`2^64` configurations), so this is not an algorithm anyone can run. The TM
model deliberately ignores this finite bound: it asks what happens
asymptotically, with unbounded memory. That idealization is what makes the
halting problem undecidable, and it is the right model for questions about
algorithms in general.

---

## 5. Putting the four models together

| Topic | Formal object | Key result | Practical face |
|---|---|---|---|
| DFA | `M = (Q, Σ, δ, q0, F)` | Kleene: DFA = NFA = regex; pumping lemma | lexers, protocols, regex |
| CFG | `G = (V, Σ, R, S)` | Chomsky hierarchy; CYK/Earley/LL/LR | parsers, compilers, JSON |
| λ-calculus | `e ::= x`, `λx. e`, or `e e` | Church–Rosser; Y; Church encodings | functional languages, closures |
| TM | `M = (Q, Γ, Σ, δ, q0, qa, qr)` | halting undecidable; Church–Turing | limits of analysis, complexity |

**The one-paragraph summary.** A DFA is computation with finite memory; it
recognizes exactly the regular languages. A context-free grammar describes
computation with a stack; it generates exactly the context-free languages,
and the Chomsky hierarchy classifies grammars by how much context their
productions may inspect. The
λ-calculus is computation with nothing but functions and substitution; it is
Turing-complete, and its Y combinator shows how recursion arises without
names. A Turing machine is computation with an unbounded tape; it defines
the recursively enumerable languages, and the halting problem shows that
this power has a hard limit. The Church–Turing thesis says that every
reasonable model of computation lands on the same class — so the limit is
not a property of Turing machines, but of computation itself.

**A dependency picture.**

```text
                 add a stack                  add a tape
   DFA  ───────────────────────►  PDA  ───────────────────────►  TM
   │                               │                              │
   │ regex                         │ CFG                          │ λ-calculus
   │                               │                              │
   regular ⊊ DCFL ⊊ CFL ⊊ CSL ⊊ recursive ⊊ RE
```

The arrows are about **memory**, not about syntax. The λ-calculus sits beside
the TM because it has the same power with a completely different surface
syntax.

---

## 6. Common misconceptions

| Misconception | Correction |
|---|---|
| "A DFA can count if it has enough states." | It can count up to a fixed bound. `{0^n 1^n}` needs unbounded counting, so it is not regular. |
| "An NFA is more powerful than a DFA." | They recognize the same class. The NFA may be exponentially smaller, but the DFA can always simulate it. |
| "A CFG can parse anything." | `{a^n b^n c^n}` is not context-free. Nesting one kind of bracket is fine; matching three independent counts is not. |
| "Ambiguity is just a cosmetic issue." | Different parse trees can mean different programs. Ambiguity is a language-design bug. |
| "The Y combinator is a recursive function." | It is a fixed-point combinator. It creates recursion by self-application; it does not call itself by name. |
| "A closure is the same as a closed term." | A closed term has no free variables; a closure is code plus a captured environment. See the table in §3.4. |
| "The halting problem says we can never know whether a program halts." | It says no single algorithm decides it for every program. Many specific programs and restricted classes are decidable. |
| "Undecidable means nobody knows the answer." | It means no algorithm can decide it in general. Each instance has a definite answer; we may still find it for special cases. |
| "The Church–Turing thesis is a theorem." | It is a hypothesis about the informal notion of effective computability. It can be refuted by a counterexample, not proved from definitions. |
| "Quantum computers compute uncomputable functions." | Under standard models they compute the same class of functions; they may change complexity, not computability. |
| "A Turing machine is a physical machine." | It is a mathematical model. Physical computers are finite approximations with finite tapes. |
| "Regex engines recognize regular languages." | Theoretical regex recognizes regular languages; engines with backreferences can recognize non-regular languages such as `{ww}`. |
| "Halting is undecidable, so testing is pointless." | Bounded halting is decidable, and many real programs are analyzable. Undecidability rules out a perfect general analyzer, not all analysis. |

---

## 7. Glossary (English–中文)

| English | 中文 | One-line meaning |
|---|---|---|
| finite state machine (FSM) | 有限狀態機 | machine with finitely many states and no workspace |
| deterministic finite automaton (DFA) | 確定性有限自動機 | FSM with exactly one move per state-symbol pair |
| nondeterministic finite automaton (NFA) | 非確定性有限自動機 | FSM that may have several moves or ε-moves |
| state transition | 狀態轉移 | change from one state to another on an input symbol |
| transition function | 轉移函數 | `δ : Q × Σ → Q` (or a relation for an NFA) |
| regular language | 正規語言 / 正則語言 | language accepted by a DFA/NFA/regex |
| pumping lemma | 泵引理／抽水引理 | necessary condition for regularity (and for CFLs) |
| grammar | 文法 | finite set of rewrite rules generating a language |
| context-free grammar (CFG) | 上下文無關文法 | grammar whose productions have one nonterminal on the left |
| context-sensitive grammar | 上下文有關文法 / 上下文敏感文法 | grammar whose rules may inspect surrounding context |
| unrestricted grammar | 無限制文法 | Type 0 grammar, as powerful as a TM |
| Chomsky hierarchy | 喬姆斯基／杭士基階層 | the four-level classification of grammars |
| Chomsky normal form (CNF) | 喬姆斯基／杭士基標準形式 | productions `A → BC` or `A → a` |
| derivation | 推導 | sequence of rewrite steps from `S` to a string |
| parse tree | 語法樹 / 剖析樹 | tree recording the structure of a derivation |
| ambiguous | 歧義的 | having more than one parse tree for some string |
| pushdown automaton (PDA) | 下推自動機 | finite automaton with a stack |
| deterministic PDA (DPDA) | 確定性下推自動機 | PDA with at most one move per configuration |
| linear-bounded automaton (LBA) | 線性有界自動機 | TM whose tape is limited to the input length |
| lambda calculus | λ 演算 | formal system of functions, application, and substitution |
| bound variable | 約束變數 | variable bound by an enclosing `λ` |
| free variable | 自由變數 | variable not bound by any `λ` |
| closed term | 封閉項 | λ-term with no free variables (a combinator) |
| closure | 閉包 / 封閉包 | code plus captured environment (or a closed term) |
| β-reduction | β-歸約 | applying `(λx. M) N` by substituting `N` for `x` |
| α-conversion | α-轉換 | renaming bound variables |
| η-conversion | η-轉換 | simplifying `λx. M x` to `M` when `x` is not free in `M` |
| normal form | 正規形式 / 範式 | term with no remaining β-redexes |
| confluence (Church–Rosser) | 合流性 | different reduction orders can be joined |
| Y combinator | Y 組合子 | fixed-point combinator that encodes recursion |
| fixed point | 不動點 | `x` such that `f x = x` |
| Church encoding | 邱奇編碼 | representing data as functions |
| Turing machine (TM) | 圖靈機 | finite control plus an unbounded tape |
| configuration | 組態 | state + tape contents + head position |
| halting problem | 停機問題 | does a TM halt on a given input? |
| decidable | 可判定 | some TM always halts with the correct yes/no answer |
| undecidable | 不可判定 | no TM decides the problem |
| recursively enumerable (RE) | 遞迴可列舉 | recognized by a TM that may loop on "no" |
| reduction | 歸約 | transforming one problem into another to transfer undecidability |
| Rice's theorem | 萊斯定理 | every nontrivial semantic property of programs is undecidable |
| Church–Turing thesis | 邱奇–圖靈論題 | effectively computable = TM-computable |
| Turing-complete | 圖靈完備 | able to simulate a universal Turing machine |
| busy beaver | 忙碌海狸 | maximal halting time of an `n`-state TM; uncomputable |

---

## 8. References

* Michael Sipser, *Introduction to the Theory of Computation*, 3rd ed.,
  Cengage, 2012. — The standard modern textbook; Chapters 1–5 cover automata,
  grammars, and decidability.
* John E. Hopcroft, Rajeev Motwani, Jeffrey D. Ullman, *Introduction to
  Automata Theory, Languages, and Computation*, 3rd ed., Pearson, 2006. —
  Detailed treatment of the Chomsky hierarchy, CYK, and closure properties.
* Noam Chomsky, "Three models for the description of language," *IRE
  Transactions on Information Theory* 2(3), 1956, pp. 113–124.
* Noam Chomsky, "On certain formal properties of grammars," *Information and
  Control* 2(2), 1959, pp. 137–167. — The original hierarchy.
* Alonzo Church, "An unsolvable problem of elementary number theory,"
  *American Journal of Mathematics* 58(2), 1936, pp. 345–363.
* Alan M. Turing, "On computable numbers, with an application to the
  Entscheidungsproblem," *Proceedings of the London Mathematical Society*
  s2-42(1), 1936, pp. 230–265; correction ibid. 43, 1937.
* Henry Gordon Rice, "Classes of recursively enumerable sets and their
  decision problems," *Transactions of the American Mathematical Society*
  74(2), 1953, pp. 358–366.
* Neil Immerman, "Nondeterministic space is closed under complementation,"
  *SIAM Journal on Computing* 17(5), 1988, pp. 935–938; Róbert Szelepcsényi,
  "The method of forcing for nondeterministic automata," *Acta Informatica*
  26(3), 1988, pp. 279–284.
* Henk P. Barendregt, *The Lambda Calculus: Its Syntax and Semantics*,
  revised ed., North-Holland, 1984.
* Benjamin C. Pierce, *Types and Programming Languages*, MIT Press, 2002. —
  Simply typed λ-calculus, strong normalization, and recursive types.
* B. Jack Copeland, "The Church–Turing Thesis," *Stanford Encyclopedia of
  Philosophy* (1997, revised) — a careful survey of the thesis, its history,
  and its variants.
* Scott Aaronson, "The Ghost in the Quantum Turing Machine," in *The Once and
  Future Turing*, Cambridge University Press, 2016 — a readable discussion of
  computation, physics, and the extended Church–Turing thesis.
* The bbchallenge collaboration, "BB(5) = 47,176,870" (2024), a verified
  proof of the fifth busy-beaver value.
* HW6 in this repository, [`../HW6/README.md`](../HW6/README.md) — a full
  λ-calculus interpreter with de Bruijn indices, normal-order and
  call-by-value reduction, traces, and a REPL.

---

## 9. About this document

This is a single-file study explainer for HW12. It contains no code files
besides the snippets embedded above. The Python blocks in each section are
meant to be run together (the `MOD3` block uses the `DFA` class, and the
Church-encoding block uses the interpreter defined just before it), and every
runnable block was executed with Python 3.12. The `D(M)` block in §4.5 is a
proof sketch, not a runnable program — its `H` is the hypothetical decider
whose existence the proof refutes. The outputs shown are the outputs of the
runs, not hand-written examples.

The four topics are presented as one story: **memory determines power, and
power has a price**. The DFA section explains what finite memory can and
cannot decide. The grammar section explains how a stack buys nesting and how
the Chomsky hierarchy organizes the result. The λ-calculus section explains
how functions alone can compute everything, and how closures and the Y
combinator make that power usable. The Turing-machine section explains why
the top of the ladder is both universal and undecidable, and why the
Church–Turing thesis makes that conclusion model-independent.

*Drafted with AI assistance (OpenCode running a large language model), using
the references in §8 and the course material in this repository. The runnable
snippets were executed and checked; corrections and improvements are
welcome.*
