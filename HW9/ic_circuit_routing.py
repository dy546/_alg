from collections import deque
import heapq

def lee_algorithm(grid, source, target):
    """
    Lee's Algorithm (BFS Grid Router for IC Routing).
    Guarantees the shortest path (minimum wire length/grid count).
    """
    rows, cols = len(grid), len(grid[0])
    distance_grid = [[-1] * cols for _ in range(rows)]
    
    # 1. Wavefront Expansion
    queue = deque([source])
    distance_grid[source[0]][source[1]] = 0
    
    found = False
    while queue:
        r, c = queue.popleft()
        if (r, c) == target:
            found = True
            break
            
        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0:
                if distance_grid[nr][nc] == -1:
                    distance_grid[nr][nc] = distance_grid[r][c] + 1
                    queue.append((nr, nc))
                    
    if not found:
        return None
        
    # 2. Backtracking
    path = [target]
    curr = target
    while curr != source:
        r, c = curr
        dist = distance_grid[r][c]
        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and distance_grid[nr][nc] == dist - 1:
                path.append((nr, nc))
                curr = (nr, nc)
                break
                
    path.reverse()
    return path

def a_star_routing(grid, source, target):
    """
    A* Routing for IC Layout. Reduces expanded search space by using Manhattan heuristic.
    """
    rows, cols = len(grid), len(grid[0])
    
    def h(pos):
        return abs(pos[0] - target[0]) + abs(pos[1] - target[1])
        
    pq = [(h(source), 0, source)]
    came_from = {}
    g_score = {source: 0}
    
    while pq:
        f, g, curr = heapq.heappop(pq)
        
        if curr == target:
            path = []
            c = target
            while c in came_from:
                path.append(c)
                c = came_from[c]
            path.append(source)
            path.reverse()
            return path
            
        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nr, nc = curr[0] + dr, curr[1] + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0:
                tentative_g = g + 1
                neighbor = (nr, nc)
                if tentative_g < g_score.get(neighbor, float('inf')):
                    g_score[neighbor] = tentative_g
                    came_from[neighbor] = curr
                    heapq.heappush(pq, (tentative_g + h(neighbor), tentative_g, neighbor))
                    
    return None

if __name__ == "__main__":
    # IC Layout Grid: 0 = Free routing space, 1 = Existing macro / blocked wire
    ic_grid = [
        [0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 0],
        [0, 1, 0, 0, 0, 1, 0],
        [0, 1, 0, 1, 0, 1, 0],
        [0, 0, 0, 1, 0, 0, 0]
    ]
    pin_a = (2, 2)
    pin_b = (4, 4)

    path_lee = lee_algorithm(ic_grid, pin_a, pin_b)
    path_astar = a_star_routing(ic_grid, pin_a, pin_b)

    print("Lee's Algorithm Wire Route:", path_lee)
    print("A* Routing Wire Route:     ", path_astar)