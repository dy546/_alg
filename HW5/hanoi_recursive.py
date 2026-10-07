def hanoi_recursive(n, source, target, auxiliary):
    if n == 1:
        print(f"Move disk 1 from {source} to {target}")
        return
    # 1. 將 n-1 個盤子從 source 搬到 auxiliary
    hanoi_recursive(n - 1, source, auxiliary, target)
    # 2. 將最大盤子從 source 搬到 target
    print(f"Move disk {n} from {source} to {target}")
    # 3. 將 n-1 個盤子從 auxiliary 搬到 target
    hanoi_recursive(n - 1, auxiliary, target, source)

# 測試 3 個盤子
print("--- 遞迴求解河內塔 ---")
hanoi_recursive(3, 'A', 'C', 'B')