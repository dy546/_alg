def hanoi_iterative(n, source, target, auxiliary):
    total_moves = (1 << n) - 1  # 2^n - 1
    
    # 根據 n 的奇偶性決定柱子輪替順序
    pegs = [source, target, auxiliary] if n % 2 != 0 else [source, auxiliary, target]
    
    # 用字典與列表模擬三個柱子（Stack 結構，內部裝盤子大小）
    state = {pegs[0]: list(range(n, 0, -1)), pegs[1]: [], pegs[2]: []}
    
    def make_legal_move(peg1, peg2):
        if not state[peg1]:
            d = state[peg2].pop()
            state[peg1].append(d)
            print(f"Move disk {d} from {peg2} to {peg1}")
        elif not state[peg2]:
            d = state[peg1].pop()
            state[peg2].append(d)
            print(f"Move disk {d} from {peg1} to {peg2}")
        elif state[peg1][-1] > state[peg2][-1]:
            d = state[peg2].pop()
            state[peg1].append(d)
            print(f"Move disk {d} from {peg2} to {peg1}")
        else:
            d = state[peg1].pop()
            state[peg2].append(d)
            print(f"Move disk {d} from {peg1} to {peg2}")

    for i in range(1, total_moves + 1):
        if i % 3 == 1:
            make_legal_move(pegs[0], pegs[1])
        elif i % 3 == 2:
            make_legal_move(pegs[0], pegs[2])
        elif i % 3 == 0:
            make_legal_move(pegs[1], pegs[2])

# 測試 3 個盤子
print("\n--- 非遞迴（迭代）求解河內塔 ---")
hanoi_iterative(3, 'A', 'C', 'B')