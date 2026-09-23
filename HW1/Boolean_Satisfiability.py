import ast
import itertools

def solve_sat_truth_table(variables, formula_str):
    try:
        tree = ast.parse(formula_str, mode="eval")
    except SyntaxError as e:
        print(f"Error: invalid formula syntax: {e}")
        return

    names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    missing = names - set(variables)
    if missing:
        print(f"Error: formula references variable(s) not in {variables}: {sorted(missing)}")
        return

    print(f"Formula: {formula_str}\n")
    
    # Header formatting
    var_header = " | ".join(f"{v:^3}" for v in variables)
    header = f"{var_header} | Result"
    print(header)
    print("-" * len(header))
    
    satisfying_assignments = []
    
    # Systematically generate all 2^N combinations (False/True)
    for combination in itertools.product([False, True], repeat=len(variables)):
        assignment = dict(zip(variables, combination))
        
        # Safely evaluate the formula under the current assignment
        result = bool(eval(formula_str, {}, assignment))
        
        # Display row
        row_str = " | ".join(f"{' T ' if assignment[v] else ' F '}" for v in variables)
        res_str = " T " if result else " F "
        print(f"{row_str} |  {res_str}")
        
        if result:
            satisfying_assignments.append(assignment)
            
    print("-" * len(header))
    if satisfying_assignments:
        print(f"Status: SATISFIABLE ({len(satisfying_assignments)} solution(s) found)\n")
        for idx, sol in enumerate(satisfying_assignments, 1):
            formatted_sol = ", ".join(f"{k}={v}" for k, v in sol.items())
            print(f"  Solution {idx}: {formatted_sol}")
    else:
        print("Status: UNSATISFIABLE\n")

if __name__ == "__main__":
    # Example 1: Satisfiable formula
    # Expression: (A or B) and (not A or C) and (not B or not C)
    vars_1 = ["A", "B", "C"]
    expr_1 = "(A or B) and (not A or C) and (not B or not C)"
    print("=== Test Case 1 ===")
    solve_sat_truth_table(vars_1, expr_1)

    print("\n" + "=" * 40 + "\n")

    # Example 2: Unsatisfiable formula (Contradiction)
    # Expression: A and not A
    vars_2 = ["A"]
    expr_2 = "A and not A"
    print("=== Test Case 2 ===")
    solve_sat_truth_table(vars_2, expr_2)