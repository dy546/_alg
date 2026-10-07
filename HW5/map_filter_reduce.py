# 自製 map
def my_map(func, lst):
    if not lst:
        return []
    return [func(lst[0])] + my_map(func, lst[1:])

# 自製 filter
def my_filter(func, lst):
    if not lst:
        return []
    head = [lst[0]] if func(lst[0]) else []
    return head + my_filter(func, lst[1:])

# 自製 reduce
def my_reduce(func, lst, initializer=None):
    if initializer is None:
        if not lst:
            raise TypeError("reduce() of empty sequence with no initial value")
        return my_reduce(func, lst[1:], lst[0])
    if not lst:
        return initializer
    return my_reduce(func, lst[1:], func(initializer, lst[0]))

def bubble_pass(arr):
    """利用 my_reduce 完成單趟冒泡，將最大值浮動到尾端，並回傳 (新陣列, 是否發生過交換)"""
    if not arr:
        return [], False
    
    def reducer(acc, item):
        res_list, swapped = acc
        if not res_list:
            return ([item], swapped)
        last_item = res_list[-1]
        if last_item > item:
            # 前者大於後者：交換兩者位置並標記 swapped = True
            return (res_list[:-1] + [item, last_item], True)
        else:
            return (res_list + [item], swapped)

    return my_reduce(reducer, arr, ([], False))

def bubble_sort_no_loops(arr):
    """完全不使用迴圈（for/while）的 Bubble Sort"""
    if len(arr) <= 1:
        return arr
    
    # 單趟冒泡處理
    new_arr, swapped = bubble_pass(arr)
    
    # 若此趟完全沒有交換，代表已完成排序，可提前終止
    if not swapped:
        return new_arr
    
    # 遞迴排序前 n-1 個元素，並拼上已就位的最後一個元素
    return bubble_sort_no_loops(new_arr[:-1]) + [new_arr[-1]]

# 測試
test_list = [64, 34, 25, 12, 22, 11, 90]
print("原始陣列:", test_list)
print("Bubble Sort 排序結果:", bubble_sort_no_loops(test_list))

# 測試自製的函數
print("my_map (x*2):", my_map(lambda x: x * 2, [1, 2, 3, 4]))
print("my_filter (偶數):", my_filter(lambda x: x % 2 == 0, [1, 2, 3, 4, 5]))
print("my_reduce (求和):", my_reduce(lambda x, y: x + y, [1, 2, 3, 4, 5]))