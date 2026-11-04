def solve_maze_dfs(maze):
    """
    Solves the Rat in a Maze problem using Depth-First Search (DFS) with Backtracking.
    
    0: Open path
    1: Wall / Obstacle
    """
    rows, cols = len(maze), len(maze[0])
    path = []
    visited = set()

    def dfs(r, c):
        # Boundary check, obstacle check, and visited check
        if r < 0 or r >= rows or c < 0 or c >= cols or maze[r][c] == 1 or (r, c) in visited:
            return False

        visited.add((r, c))
        path.append((r, c))

        # Reached destination (bottom-right corner)
        if (r, c) == (rows - 1, cols - 1):
            return True

        # Direction vectors: Down, Right, Up, Left
        directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        for dr, dc in directions:
            if dfs(r + dr, c + dc):
                return True

        # Backtrack
        path.pop()
        return False

    success = dfs(0, 0)
    return success, path

def print_grid_with_path(maze, path):
    grid = [row[:] for row in maze]
    if path:
        for r, c in path:
            grid[r][c] = "*"
    for row in grid:
        print(" ".join(str(cell) for cell in row))

if __name__ == "__main__":
    sample_maze = [
        [0, 1, 0, 0, 0],
        [0, 1, 0, 1, 0],
        [0, 0, 0, 1, 0],
        [1, 1, 0, 0, 0],
        [0, 0, 0, 1, 0]
    ]

    found, solution_path = solve_maze_dfs(sample_maze)
    if found:
        print("Path found (marked with *):")
        print_grid_with_path(sample_maze, solution_path)
        print("Coordinates:", solution_path)
    else:
        print("No path exists.")