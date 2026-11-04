from collections import deque

def is_valid_state(state):
    """
    State format: (Farmer, Wolf, Goat, Cabbage)
    Values: 0 = Left bank, 1 = Right bank
    """
    f, w, g, c = state
    # Wolf and Goat left alone without Farmer
    if w == g and f != w:
        return False
    # Goat and Cabbage left alone without Farmer
    if g == c and f != g:
        return False
    return True

def solve_river_crossing_bfs():
    """
    Finds the shortest sequence of state transitions to cross the river using BFS.
    """
    start = (0, 0, 0, 0)
    goal = (1, 1, 1, 1)

    queue = deque([(start, [start])])
    visited = {start}

    item_names = ["Farmer", "Wolf", "Goat", "Cabbage"]

    while queue:
        current, path = queue.popleft()
        if current == goal:
            return path

        f, w, g, c = current
        candidates = []

        # 1. Farmer crosses alone
        candidates.append((1 - f, w, g, c))
        # 2. Farmer crosses with Wolf
        if f == w:
            candidates.append((1 - f, 1 - w, g, c))
        # 3. Farmer crosses with Goat
        if f == g:
            candidates.append((1 - f, w, 1 - g, c))
        # 4. Farmer crosses with Cabbage
        if f == c:
            candidates.append((1 - f, w, g, 1 - c))

        for nxt in candidates:
            if is_valid_state(nxt) and nxt not in visited:
                visited.add(nxt)
                queue.append((nxt, path + [nxt]))

    return None

def describe_transition(state_a, state_b):
    bank = "Right" if state_b[0] == 1 else "Left"
    moved = []
    names = ["Farmer", "Wolf", "Goat", "Cabbage"]
    for i in range(1, 4):
        if state_a[i] != state_b[i]:
            moved.append(names[i])
    if moved:
        return f"Farmer takes {moved[0]} to the {bank} bank."
    return f"Farmer returns to the {bank} bank alone."

if __name__ == "__main__":
    path = solve_river_crossing_bfs()
    print(f"Optimal Solution ({len(path) - 1} steps):\n")
    for step_num, (state_a, state_b) in enumerate(zip(path[:-1], path[1:]), start=1):
        print(f"Step {step_num}: {describe_transition(state_a, state_b)}")