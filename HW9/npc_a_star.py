import heapq

def heuristic(a, b):
    # Manhattan distance
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star_npc(grid, start, goal):
    """
    Finds optimal path for NPC to reach player using A* Search.
    
    0: Standard floor (movement cost = 1)
    1: Wall / Obstacle (Impassable)
    5: Swamp / Mud (movement cost = 5)
    """
    rows, cols = len(grid), len(grid[0])
    
    open_heap = []
    heapq.heappush(open_heap, (heuristic(start, goal), 0, start))
    
    came_from = {}
    g_score = {start: 0}
    nodes_explored = 0

    while open_heap:
        f, current_g, current = heapq.heappop(open_heap)
        nodes_explored += 1

        if current == goal:
            # Reconstruct path
            path = []
            curr = goal
            while curr in came_from:
                path.append(curr)
                curr = came_from[curr]
            path.append(start)
            path.reverse()
            return path, g_score[goal], nodes_explored

        if current_g > g_score.get(current, float('inf')):
            continue

        r, c = current
        for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != 1:
                step_cost = grid[nr][nc] if grid[nr][nc] > 0 else 1
                tentative_g = current_g + step_cost
                neighbor = (nr, nc)

                if tentative_g < g_score.get(neighbor, float('inf')):
                    g_score[neighbor] = tentative_g
                    came_from[neighbor] = current
                    f_score = tentative_g + heuristic(neighbor, goal)
                    heapq.heappush(open_heap, (f_score, tentative_g, neighbor))

    return None, float('inf'), nodes_explored

if __name__ == "__main__":
    # 0 = Normal, 1 = Wall, 5 = Swamp
    map_grid = [
        [0, 0, 0, 0, 0],
        [1, 1, 0, 1, 0],
        [0, 5, 5, 1, 0],
        [0, 1, 1, 1, 0],
        [0, 0, 0, 0, 0]
    ]
    npc_pos = (0, 0)
    player_pos = (4, 4)

    path, total_cost, explored = a_star_npc(map_grid, npc_pos, player_pos)
    print(f"Optimal Path found: {path}")
    print(f"Total Movement Cost: {total_cost}")
    print(f"Total Nodes Explored: {explored}")