# Graph Search and Pathfinding Algorithms Suite

This repository implements key classical search algorithms (DFS, BFS, A*, and IC Circuit Routing methods) applied to classic benchmark problems in computer science and Electronic Design Automation (EDA).

---

## Table of Contents
1. [Rat in a Maze (DFS)](#1-rat-in-a-maze-dfs)
2. [Wolf, Goat, and Cabbage River Crossing (BFS)](#2-wolf-goat-and-cabbage-river-crossing-bfs)
3. [8-Queens Problem (DFS)](#3-8-queens-problem-dfs)
4. [NPC Pathfinding to Player (A*)](#4-npc-pathfinding-to-player-a)
5. [IC Design Circuit Routing Algorithms](#5-ic-design-circuit-routing-algorithms)
6. [Algorithmic Complexity Summary](#algorithmic-complexity-summary)
7. [Running the Code](#running-the-code)

---

## 1. Rat in a Maze (DFS)
* **File**: `1_rat_in_a_maze.py`
* **Algorithm**: Depth-First Search (DFS) with Backtracking.
* **Problem Overview**: A rat starts at `(0, 0)` on an $M \times N$ grid and must reach the exit at `(M-1, N-1)`. Certain grid cells are blocked walls (`1`).
* **Search Strategy**: 
  * DFS explores deeply down one candidate path until it reaches either the target or a dead end.
  * When a dead end is hit, backtracking removes the current cell from the solution path and explores alternate direction vectors (Down, Right, Up, Left).

---

## 2. Wolf, Goat, and Cabbage River Crossing (BFS)
* **File**: `2_wolf_goat_cabbage.py`
* **Algorithm**: Breadth-First Search (BFS).
* **Problem Overview**: A farmer must transport a wolf, a goat, and a cabbage across a river using a boat that holds only the farmer and one item. 
  * If left alone without the farmer: Wolf eats Goat, or Goat eats Cabbage.
* **Search Strategy**:
  * States are represented as tuples `(Farmer, Wolf, Goat, Cabbage)` where `0` denotes the left bank and `1` the right bank.
  * BFS guarantees finding the **shortest possible sequence of transitions** (7 moves).
  * Valid next states are appended to a queue while avoiding unsafe configurations and previously visited states.

---

## 3. 8-Queens Problem (DFS)
* **File**: `3_eight_queens.py`
* **Algorithm**: Depth-First Search (DFS) / Backtracking.
* **Problem Overview**: Place 8 non-attacking queens on an $8 \times 8$ chessboard (no two queens share the same row, column, or diagonal).
* **Search Strategy**:
  * Places queens row-by-row (`row 0` to `row 7`).
  * For each row, tests columns `0` through `7` for conflicts against previously placed queens:
    * Column collision: `col == prev_col`
    * Diagonal collision: `|col - prev_col| == |row - prev_row|`
  * Systematically explores all 92 valid configurations.

---

## 4. NPC Pathfinding to Player (A*)
* **File**: `4_npc_a_star.py`
* **Algorithm**: $A^*$ Search Algorithm.
* **Problem Overview**: Game AI where a Non-Player Character (NPC) must navigate dynamic terrain (obstacles, open ground, high-cost swamps) to reach a moving player.
* **Search Strategy**:
  * Evaluates nodes using $f(n) = g(n) + h(n)$:
    * $g(n)$: Exact path cost accumulated from the start node to $n$.
    * $h(n)$: Estimated cost from $n$ to the destination (Manhattan Distance: $|x_1 - x_2| + |y_1 - y_2|$).
  * Priority queue (min-heap) expands nodes with the lowest $f(n)$ value, guaranteeing optimal pathfinding while minimizing node expansions compared to BFS or Dijkstra.

---

## 5. IC Design Circuit Routing Algorithms
* **File**: `5_ic_circuit_routing.py`
* **Context**: Electronic Design Automation (EDA) VLSI layout routing, connecting pin nets across physical chip grid layers while avoiding macro blockages and design rule violations.

### Comparison of Circuit Routing Algorithms

| Routing Algorithm | Core Mechanism | Optimality (Wire Length) | Search Space / Speed | Best Suited For |
| :--- | :--- | :--- | :--- | :--- |
| **Lee's Algorithm** | Breadth-First Search (Wavefront expansion) | **Guaranteed Shortest** | High memory & runtime $O(M \times N)$ | Global/Detailed grid routing where exact minimum wire length is mandatory. |
| **$A^*$ Routing** | Best-First Search with Manhattan/Euclidean $h(n)$ | **Guaranteed Shortest** (if $h(n)$ is admissible) | Significantly smaller search space than Lee | Standard point-to-point pin routing in cell placement & EDA layout. |
| **Soukup's Algorithm** | Combined Line Search (DFS) + Wave Expansion (BFS) | Near-optimal (Sub-optimal in dense areas) | Extremely fast for simple or unblocked layouts | Large-scale IC layouts with sparse blockages requiring rapid wire creation. |
| **Hadlock's Algorithm** | Detour Number Search $d(n) = \text{cost} + \text{detour}$ | **Guaranteed Shortest** | Fast expansion towards target, bounded search space | Detailed routing in grid-based multilayer IC structures with minimal detours. |

#### Detailed Methodology Breakdown:

1. **Lee's Algorithm (Wavefront Maze Router)**
   * **Phase 1 (Expansion)**: Starting from Source pin $S$, labels neighboring grid cells with distance numbers $1, 2, 3, \dots$ until Target pin $T$ is reached.
   * **Phase 2 (Backtracking)**: Traces back from $T$ to $S$ by walking strictly along monotonically decreasing values ($d, d-1, d-2 \dots$).
   * *Trade-off*: Memory footprint is large ($O(N \times M)$ grid entries per net).

2. **$A^*$ Routing Algorithm**
   * Uses heuristic estimate $h(n) = |x_n - x_T| + |y_n - y_T|$. Directs wavefront toward the target pin, reducing node expansion by up to 90% in sparse IC regions.

3. **Soukup's Fast Router**
   * Drives a straight line (DFS-style line search) directly toward the target until an obstacle is encountered.
   * When blocked, switches to Lee-style BFS expansion until a new unobstructed path line toward the target is found, then resumes line search.

4. **Hadlock's Detour Algorithm**
   * Defines detour index: moving away from target increases detour count by $+1$; moving toward target adds $+0$.
   * Searches nodes in increasing order of detour costs, finding shortest paths with far fewer cell explorations than standard BFS.

---

## Algorithmic Complexity Summary

| Problem / Domain | Algorithm Used | Time Complexity | Space Complexity |
| :--- | :--- | :--- | :--- |
| **Rat in a Maze** | DFS Backtracking | $O(4^{V}) \approx O(M \times N)$ | $O(M \times N)$ |
| **River Crossing** | BFS | $O(V + E)$ state graph | $O(V)$ |
| **8-Queens** | DFS Backtracking | $O(N!)$ | $O(N)$ recursion depth |
| **NPC Pathfinding** | $A^*$ Search | $O(E \log V)$ worst case | $O(V)$ |
| **IC Grid Routing** | Lee's Algorithm (BFS) | $O(M \times N)$ | $O(M \times N)$ |
| **IC Grid Routing** | $A^*$ Search | $O(E \log V)$ | $O(V)$ |

---

## Running the Code

Ensure Python 3.8+ is installed. Execute any script directly:

```bash
python 1_rat_in_a_maze.py
python 2_wolf_goat_cabbage.py
python 3_eight_queens.py
python 4_npc_a_star.py
python 5_ic_circuit_routing.py