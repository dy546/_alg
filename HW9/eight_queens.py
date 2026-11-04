def solve_n_queens(n=8):
    """
    Solves the 8-Queens problem using DFS with Backtracking.
    """
    solutions = []

    def is_safe(board, row, col):
        for prev_row in range(row):
            prev_col = board[prev_row]
            if prev_col == col or abs(prev_col - col) == abs(prev_row - row):
                return False
        return True

    def dfs(row, current_board):
        if row == n:
            solutions.append(list(current_board))
            return

        for col in range(n):
            if is_safe(current_board, row, col):
                current_board.append(col)
                dfs(row + 1, current_board)
                current_board.pop()

    dfs(0, [])
    return solutions

def print_board(solution):
    n = len(solution)
    for row in range(n):
        line = ["Q" if col == solution[row] else "." for col in range(n)]
        print(" ".join(line))
    print()

if __name__ == "__main__":
    solutions = solve_n_queens(8)
    print(f"Total valid configurations found: {len(solutions)}\n")
    print("First Solution Representation:")
    print_board(solutions[0])